from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from django.db import transaction
from .models import User, Profile




# Login Serializer
class UserLoginSerializer(LoginSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)


# User Registration Serializer
class CustomRegisterSerializer( RegisterSerializer):
    username = serializers.CharField(
        max_length = 20,
        min_length = 5,
        validators = [
            lambda value: None if ' ' not in value else serializers.ValidationError("Username cannot contain spaces")]
    )
    email = serializers.EmailField(required = True)
    password1 = serializers.CharField(write_only = True, required = True,
                                      validators = [validate_password])
    password2 = serializers.CharField(write_only = True, required = True, )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        extra_kwargs = {'password': {'write_only': True}}
    def validate(self, attrs):
        if attrs['password1'] != self.initial_data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return attrs

    def create(self, validated_data):
        try:
            user = User.objects.create(
                email = validated_data['email'],
                username = validated_data.get['username'],  # Optional username
            )
            user.set_password(validated_data['password'])
            user.save()

            return user
        except IntegrityError:
            raise serializers.ValidationError({"email": "This email is already in use."})


# User Profile Serializer
class ProfileSerializer(CountryFieldMixin ,serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields =['phone', 'country', 'profile_image', 'github_link', 'linkedin_link']
        extra_kwargs = {
            'phone': {'required': False},
            'country': {'required': False},
            'profile_image': {'required': False},
            'github_link': {'required': False},
            'linkedin_link': {'required': False},
        }
class UserProfileSerializer( UserDetailsSerializer):
    userprofile= ProfileSerializer()
    class Meta:
        model = User
        fields = ['username', 'email','userprofile']
        read_only_fields = ['email']


    def update(self, instance, validated_data):
        profile_data = validated_data.pop('userprofile', {})
        # Update User fields
        instance = super().update(instance, validated_data)

        # Update Profile fields
        if profile_data and hasattr(instance, 'userprofile'):
            for attr, value in profile_data.items():
                setattr(instance.userprofile, attr, value)
            instance.userprofile.save()

        return instance
