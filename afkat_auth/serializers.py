from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.validators import UniqueValidator

from afkat_auth.permissions import UserIsOwnerOrReadOnly
from .models import User, Profile


class UserLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(
        max_length=20,
        min_length=5,
        validators=[
            lambda value: None
            if " " not in value
            else serializers.ValidationError("Username cannot contain spaces")
        ],
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message=_("A user with this email already exists")),]
    )

    password1 = None
    password2 = None

    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != self.initial_data["confirm_password"]:
            raise serializers.ValidationError({"error":"The two password fields didn't match"})
        return attrs

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "email": self.validated_data.get("email", ""),
            "password": self.validated_data.get("password", ""),
        }

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
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

    class Meta:
        model = User
        fields = ["username", "email", "userProfile"]
        read_only_fields = ["email"]
        extra_kwargs = {
            "username" : {"required":False},
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
