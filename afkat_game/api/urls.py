import requests
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from afkat_game.api.views import (
    GameViewSet,
    GameCommentViewSet,
    GameRatingViewSet,
    GameJamViewSet,
    get_game_share_links,
    AFKGatewayView,
)

router = DefaultRouter()
router.register(r"comments", GameCommentViewSet)
router.register(r"ratings", GameRatingViewSet)
router.register(r"jams", GameJamViewSet)
router.register(r"", GameViewSet)

app_name = "afkat_game_api"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:game_pk>/share/",
        get_game_share_links,
        name="game-share-links",
    ),
    re_path(r"^afk-service(?:/.*)?$", AFKGatewayView.as_view()),
    # path("achivement_id/<int:achievement_id>", get_achievments,name='achivement_id_get'),  # New endpoint
]
