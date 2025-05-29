from django.urls import path, include
from rest_framework.routers import DefaultRouter
from afkat_game.api.views import (
    GameViewSet,
    GameCommentViewSet,
    GameRatingViewSet,
    GameJamViewSet,
    get_game_share_links,
    get_leaderboard,
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
    path(
        "leaderboard/<int:leaderboard_id>", get_leaderboard, name="leaderboard-by-id"
    ),
]
