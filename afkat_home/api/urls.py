from django.urls import path, include
from rest_framework.routers import DefaultRouter
from afkat_home.api.views import PostViewSet


router = DefaultRouter()
# router.register("tags", TagViewSet)
router.register(
    "posts", PostViewSet
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/by-time/<str:period_name>/",
        PostViewSet.as_view({"get": "list"}),
        name="posts-by-time",
    ),

]

