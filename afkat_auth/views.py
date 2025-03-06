from django.core.serializers import serialize
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import  RefreshToken
from .serializers import UserRegistrationSerializer , LoginSerializer
from django.contrib.auth import authenticate  , login
from django.utils.decorators import method_decorator
from django.contrib import messages

# Create your views here.
@login_required
def profile(request):
    return render(request, "afkat_auth/profile.html")


@method_decorator(csrf_exempt, name = "dispatch")
class CustomLoginView(APIView):
    def post(self , request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        # Authenticate user
        user = authenticate(request , username = email, password = password)

        if user is not None:
            # Login the user (optional, depends on your session management)
            login(request, user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id ,
                    'email': user.email,
                }
            }, status = status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'},
                        status = status.HTTP_401_UNAUTHORIZED)


# @method_decorator(csrf_exempt , name = "dispatch")
class CustomRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            }, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)