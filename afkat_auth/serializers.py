from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import User
from django.contrib.auth.password_validation import validate_password

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True , required =  True , validators = [validate_password])
    confirm_password = serializers.CharField(write_only=True , required =  True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password' , 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                username=validated_data['username'],
            )
            return user
        except Exception as e:
            raise ("user registration failed", str(e))
