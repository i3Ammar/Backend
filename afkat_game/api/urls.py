from django.urls import path , include
from rest_framework.routers import DefaultRouter
from afkat_game.api.views import GameViewSet  , GameCommentViewSet , GameRatingViewSet

router = DefaultRouter()
router.register(r'games',GameViewSet)
router.register(r'comments',GameCommentViewSet)
router.register(r'ratings',GameRatingViewSet)


urlpatterns  = [
    path('',include(router.urls)),
]