from dj_rest_auth.registration.serializers import RegisterSerializer, get_adapter, setup_user_email
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from afkat.utils.serializer_field import CompressedImageField
from afkat_auth.permissions import UserIsOwnerOrReadOnly
from .models import User, Profile, Follow


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user) -> Token:
        token = super().get_token(user)
        token['username'] = user.username
        return token


class UserLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(
        max_length = 20,
        min_length = 5,
        validators = [
            lambda value: None
            if " " not in value
            else serializers.ValidationError({'error': "Username cannot contain spaces"})
        ],
    )
    email = serializers.EmailField(
        validators = [
            UniqueValidator(queryset = User.objects.all(), message = _("A user with this email already exists")), ]
    )

    password1 = None
    password2 = None

    password = serializers.CharField(write_only = True, validators = [validate_password])
    confirm_password = serializers.CharField(
        write_only = True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != self.initial_data["confirm_password"]:
            raise serializers.ValidationError({"error": "The two password fields didn't match"})
        return attrs

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "email": self.validated_data.get("email", ""),
            "password": self.validated_data.get("password", ""),
        }

    def save(self, request):
        with transaction.atomic():
            adapter = get_adapter()
            user = adapter.new_user(request)
            self.cleaned_data = self.get_cleaned_data()
            user = adapter.save_user(request, user, self, commit = False)
            if "password" in self.cleaned_data:
                try:
                    adapter.clean_password(self.cleaned_data['password'], user = user)
                except DjangoValidationError as exc:
                    raise serializers.ValidationError(
                        detail = serializers.as_serializer_error(exc)
                    )

            user.save()
            self.custom_signup(request, user)
            setup_user_email(request, user, [])
            return user


class ProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):

    profile_image = CompressedImageField(
        max_size=1200,
        quality=80,
        maintain_format=True,
        max_file_size_kb=500
    )
    class Meta:
        model = Profile
        fields = ["phone", "country", "profile_image", "github_link", "linkedin_link"]
        extra_kwargs = {
            "phone": {"required": False},
            "country": {"required": False},
            "profile_image": {"required": False},
            "github_link": {"required": False},
            "linkedin_link": {"required": False},
        }


class UserProfileSerializer(UserDetailsSerializer):
    userProfile = ProfileSerializer()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', "username", "email", "userProfile", "followers_count", "following_count", "is_following"]
        read_only_fields = ["email", "followers_count", "following_count", "is_following"]
        extra_kwargs = {
            "username": {"required": False},
        }

    @permission_classes(UserIsOwnerOrReadOnly)
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("userProfile", {})
        instance = super().update(instance, validated_data)

        if profile_data and hasattr(instance, "userProfile"):
            for attr, value in profile_data.items():
                setattr(instance.userProfile, attr, value)
            instance.userProfile.save()

        return instance

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower = request.user, following = obj).exists()
        return False


class FollowSerializer(serializers.Serializer):
    follower = serializers.ReadOnlyField(source = 'follower.username')
    following = serializers.ReadOnlyField(source = 'following.username')

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
