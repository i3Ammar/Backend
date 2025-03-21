from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from afkat_auth.views import UserDetail

urlpatterns = [
    path("auth/", include("rest_framework.urls")),
    path("", include("dj_rest_auth.urls")),
    path("register/", include("dj_rest_auth.registration.urls")),
    path("users/<int:pk>", UserDetail.as_view(), name="api_user_detail"),
]
