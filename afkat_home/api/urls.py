from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PostViewSet,
    get_post_share_links,
)

app_name = "afkat_home_api"

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls) , name = "post-detail"),
    path('posts/<int:post_pk>/share/', get_post_share_links, name = 'post-share-links'),

]
