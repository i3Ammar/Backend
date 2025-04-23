from django.urls import include, path
from rest_framework.routers import DefaultRouter
from afkat_art.api.views import ArtViewSet

router = DefaultRouter()
router.register(r'art',ArtViewSet)

urlpatterns = [
    path('',include ( router.urls ))
]