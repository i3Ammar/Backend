
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate  , login
from django.utils.decorators import method_decorator

from rest_framework.permissions import  IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import  RefreshToken

from afkat_auth.serializers import  LoginSerializer, UserProfileSerializer

from afkat_auth.models import User

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
# class CustomRegistrationView(APIView):
#     def post(self, request):
#         serializer = UserRegistrationSerializer(data = request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#
#             return Response({
#                 'user': {
#                     'id': user.id,
#                     'username': user.username,
#                     'email': user.email,
#                 }
#             }, status = status.HTTP_201_CREATED)
#         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser , FormParser ]
    http_method_names = ['get','patch','head','options']

    def get_queryset(self):
        return User.objects.filter(pk = self.request.user.pk)

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data = request.data, partial = True)
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)
        return Response(serializer.data)

