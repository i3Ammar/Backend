from django.urls import path , include
from rest_framework.routers import DefaultRouter
from afkat_game.api.views import GameViewSet, GameCommentViewSet, GameRatingViewSet, GameJamViewSet

router = DefaultRouter()
router.register(r'comments',GameCommentViewSet)
router.register(r'ratings',GameRatingViewSet)
router.register(r'jams' , GameJamViewSet)
router.register(r'',GameViewSet)


urlpatterns  = [
    path('',include(router.urls)),
]