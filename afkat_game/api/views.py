# afkat_game/api/views.py
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .filters import GameFilter
from afkat_game.api.serializers import (
    GameCommentSerializer,
    GameDetailSerializer,
    GameRatingSerializer,
)
from afkat_game.models import Game, GameComments, GameRating


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = GameFilter
    search_fields = ['title']


    def perform_destroy(self, instance):
        if instance.creator == self.request.user:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You dont have permission to delete this Game .")

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def comment(self, request, pk=None):
        game = self.get_object()
        serializer = GameCommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, game=game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def rate(self, request, pk=None):
        game = self.get_object()

        try:
            rating = GameRating.objects.get(user=request.user, game=game)
            serializer = GameRatingSerializer(rating, data=request.data)
        except GameRating.DoesNotExist:
            serializer = GameRatingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, game=game)
            game.refresh_from_db()
            return Response({"rating": serializer.data, "game_avg_rating": game.rating})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=True, url_path="download")
    def download_game(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        game.download_count += 1
        game.save(update_fields=["download_count"])
        response = FileResponse(
            game.game_file.open(), as_attachment=True, filename=game.game_file.name
        )
        return response


class GameCommentViewSet(viewsets.ModelViewSet):
    queryset = GameComments.objects.all()
    serializer_class = GameCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GameRatingViewSet(viewsets.ModelViewSet):
    queryset = GameRating.objects.all()
    serializer_class = GameRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
