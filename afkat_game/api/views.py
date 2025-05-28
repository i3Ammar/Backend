import requests
from django.db import transaction
from django.http import FileResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView



from afkat_game.api.serializers import (
    GameCommentSerializer,
    GameDetailSerializer,
    GameRatingSerializer,
    GameJamSerializer,
    GameJamParticipationSerializer,
)
from afkat_game.models import Game, GameComments, GameRating, GameJam
from afkat_home.api.serializers import AuthorSerializer
from .filters import GameFilter
from ..services.game_service import validate_game_file, validate_cover_image, process_webgl_upload

from afkat_art.api.pagination import GameAndArtLayoutPagination

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().select_related('creator').prefetch_related('tags')
    serializer_class = GameDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser , JSONParser]
    pagination_class = GameAndArtLayoutPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = GameFilter
    search_fields = ['title']
    ordering_fields = ['title', 'created_at']
    ordering = ['?']

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        validate_cover_image(self , serializer.validated_data['thumbnail'])
        validate_game_file(self, serializer.validated_data['game_file'])
        # game = serializer.save(creator = self.request.user)
        serializer.save()
        #FIXME  dont forget to remove the comments  when deploy
        # relative_path = process_webgl_upload(
        #     serializer.validated_data['game_file'],
        #     game.id
        # )
        # game.webgl_index_path = relative_path
        # game.save(update_fields = ['webgl_index_path'])

    def perform_destroy(self, instance):
        if instance.creator == self.request.user:
            instance.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You dont have permission to delete this Game .")

    @action(detail = True, methods = ["post"], permission_classes = [permissions.IsAuthenticated])
    def comment(self, request, pk = None):
        game = self.get_object()
        serializer = GameCommentSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save(user = request.user, game = game)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail = True, methods = ["get"], permission_classes = [permissions.IsAuthenticated])
    def comments(self, request, pk = None):
        game = self.get_object()
        comments = GameComments.objects.filter(game = game).select_related('user')
        serializer = GameCommentSerializer(comments, many = True)
        return Response(serializer.data)

    @action(detail = True, methods = ["post"], permission_classes = [permissions.IsAuthenticated])
    def rate(self, request, pk = None):
        game = self.get_object()

        try:
            rating = GameRating.objects.get(user = request.user, game = game)
            serializer = GameRatingSerializer(rating, data = request.data)
        except GameRating.DoesNotExist:
            serializer = GameRatingSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save(user = request.user, game = game)
            game.refresh_from_db()
            return Response({"rating": serializer.data, "game_avg_rating": game.rating})
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(methods = ["get"], detail = True, url_path = "download")
    def download_game(self, request, pk = None):
        game = get_object_or_404(Game, pk = pk)
        game.download_count += 1
        game.save(update_fields = ["download_count"])
        response = FileResponse(
            game.game_file.open("rb"), as_attachment = True, filename = game.game_file.name
        )
        return response


class GameCommentViewSet(viewsets.ModelViewSet):
    queryset = GameComments.objects.all().select_related('user', 'game')
    serializer_class = GameCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


class GameRatingViewSet(viewsets.ModelViewSet):
    queryset = GameRating.objects.all().select_related('user', 'game')
    serializer_class = GameRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


class GameJamViewSet(viewsets.ModelViewSet):
    queryset = GameJam.objects.all().select_related('created_by').prefetch_related('participants', 'submitted_games')
    serializer_class = GameJamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = GameJam.objects.all().select_related('created_by').prefetch_related('participants', 'submitted_games')

        status = self.request.query_params.get('status')
        if status:
            now = timezone.now()
            if status == 'active':
                queryset = queryset.filter(start_date__lte = now, end_date__gte = now)
            elif status == 'upcoming':
                queryset = queryset.filter(start_date__gt = now)
            elif status == 'past':
                queryset = queryset.filter(end_date__lt = now)

        participation = self.request.query_params.get('participation')
        if participation and self.request.user.is_authenticated:
            if participation == 'participating':
                queryset = queryset.filter(participants = self.request.user)
            elif participation == 'created':
                queryset = queryset.filter(created_by = self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)

    @action(detail = True, methods = ['post'], permission_classes = [permissions.IsAuthenticated])
    def participate(self, request, pk = None):
        game_jam = self.get_object()
        serializer = GameJamParticipationSerializer(
            data = request.data,
            context = {'request': request, 'game_jam': game_jam}
        )

        if serializer.is_valid():
            serializer.save()  # This will call the service functions
            action = serializer.validated_data['action']
            return Response({'status': f'{action}ed game jam'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @method_decorator(cache_page(60 * 10))
    @action(detail = True, methods = ['get'])
    def participants(self, request, pk = None):
        game_jam = self.get_object()

        participants = game_jam.participants.all()
        serializer = AuthorSerializer(participants, many = True, context = {'request': request})

        return Response(serializer.data)

    @action(detail = True, methods = ['post'], permission_classes = [permissions.IsAuthenticated])
    def submit_game(self, request, pk = None):
        game_jam = self.get_object()

        if not game_jam.participants.filter(id = request.user.id).exists():
            raise PermissionDenied("You must be a participant to submit a game")

        game = get_object_or_404(Game, pk = request.data.get('game_id'))

        if game.creator != request.user:
            raise PermissionDenied("You can only submit your own games")

        game_jam.submitted_games.add(game)
        return Response({'status': 'game submitted successfully'})

# class LeaderBoardViewSet(APIView) :
#     def get(self, request):
#         permissions = [permissions.IsAuthenticated]
#         response = requests.get('fakeURL')
#         return Response(response.json())


