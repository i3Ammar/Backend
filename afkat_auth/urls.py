from django.urls import include, path

from afkat_auth.views import UserDetail

urlpatterns = [
    path("rest_auth/", include("rest_framework.urls")),
    path("", include("dj_rest_auth.urls")),
    path("register/", include("dj_rest_auth.registration.urls")),
    path("users/<int:pk>", UserDetail.as_view(), name="api_user_detail"),
]
