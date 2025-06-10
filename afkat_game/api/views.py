import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.http import FileResponse, HttpResponseRedirect, JsonResponse, HttpRequest, HttpResponse
from django.views import View
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from urllib.parse import urlencode, quote_plus
from django.urls import NoReverseMatch
from django.http import HttpRequest
from sentry_sdk.integrations.beam import raise_exception

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
from ..services.game_service import (
    validate_game_file,
    validate_cover_image,
    process_webgl_upload,
)

from afkat_art.api.pagination import GameAndArtLayoutPagination


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().select_related("creator").prefetch_related("tags")
    serializer_class = GameDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = GameAndArtLayoutPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = GameFilter
    search_fields = ["title"]
    ordering_fields = ["title", "created_at"]
    ordering = ["-created_at"]

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = self.get_object()

        if 'thumbnail' in serializer.validated_data:
            validate_cover_image(self, serializer.validated_data["thumbnail"])

        if 'game_file_win' in serializer.validated_data:
            validate_game_file(self, serializer.validated_data["game_file_win"])

        if 'game_file' in serializer.validated_data:
            validate_game_file(self, serializer.validated_data["game_file"])
            if instance.game_file != serializer.validated_data["game_file"]:
                relative_path = process_webgl_upload(
                    serializer.validated_data["game_file"], instance.id
                )
                serializer.save(webgl_index_path = relative_path)
                return

        serializer.save()
    @transaction.atomic
    def perform_create(self, serializer):
        validate_cover_image(self, serializer.validated_data["thumbnail"])
        validate_game_file(self, serializer.validated_data["game_file_win"])
        validate_game_file(self, serializer.validated_data["game_file"])
        game = serializer.save(creator=self.request.user)
        # serializer.save()
        relative_path = process_webgl_upload(
            serializer.validated_data["game_file"], game.id
        )
        game.webgl_index_path = relative_path
        game.save(update_fields=["webgl_index_path"])

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
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def comments(self, request, pk=None):
        game = self.get_object()
        comments = GameComments.objects.filter(game=game).select_related("user")
        serializer = GameCommentSerializer(comments, many=True)
        return Response(serializer.data)

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
        game.download_count += F("download_count") + 1
        game.save(update_fields=["download_count"])
        response = FileResponse(
            game.game_file.open("rb"), as_attachment=True, filename=game.game_file.name
        )
        return response


class GameCommentViewSet(viewsets.ModelViewSet):
    queryset = GameComments.objects.all().select_related("user", "game")
    serializer_class = GameCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GameRatingViewSet(viewsets.ModelViewSet):
    queryset = GameRating.objects.all().select_related("user", "game")
    serializer_class = GameRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GameJamViewSet(viewsets.ModelViewSet):
    queryset = (
        GameJam.objects.all()
        .select_related("created_by")
        .prefetch_related("participants", "submitted_games")
    )
    serializer_class = GameJamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        status = self.request.query_params.get("status")
        if status:
            now = timezone.now()
            if status == "active":
                queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
            elif status == "upcoming":
                queryset = queryset.filter(start_date__gt=now)
            elif status == "past":
                queryset = queryset.filter(end_date__lt=now)

        participation = self.request.query_params.get("participation")
        if participation and self.request.user.is_authenticated:
            if participation == "participating":
                queryset = queryset.filter(participants=self.request.user)
            elif participation == "created":
                queryset = queryset.filter(created_by=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def participate(self, request, pk=None):
        game_jam = self.get_object()
        serializer = GameJamParticipationSerializer(
            data=request.data, context={"request": request, "game_jam": game_jam}
        )

        if serializer.is_valid():
            serializer.save()  # This will call the service functions
            action = serializer.validated_data["action"]
            return Response({"status": f"{action}ed game jam"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(cache_page(60 * 10))
    @action(detail=True, methods=["get"])
    def participants(self, request, pk=None):
        game_jam = self.get_object()

        participants = game_jam.participants.all()
        serializer = AuthorSerializer(
            participants, many=True, context={"request": request}
        )

        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def submit_game(self, request, pk=None):
        game_jam = self.get_object()

        if not game_jam.participants.filter(id=request.user.id).exists():
            raise PermissionDenied("You must be a participant to submit a game")

        game = get_object_or_404(Game, pk=request.data.get("game_id"))

        if game.creator != request.user:
            raise PermissionDenied("You can only submit your own games")

        game_jam.submitted_games.add(game)
        return Response({"status": "game submitted successfully"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_game_share_links(request: HttpRequest, game_pk: int):
    """
    Generates social media sharing links for a given game.
    """
    try:
        game = get_object_or_404(Game, pk=game_pk)
        game_url = request.build_absolute_uri(game.get_absolute_url())
        game_title = quote_plus(game.title)

        share_links = {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={game_url}",
            "twitter": f"https://twitter.com/intent/tweet?url={game_url}&text={game_title}",
            "linkedin": f"https://www.linkedin.com/shareArticle?mini=true&url={game_url}&title={game_title}",
            "email": f"mailto:?subject={game_title}&body={game_url}",
            "whatsapp": f"https://api.whatsapp.com/send?text={game_title}%20{game_url}",
            "telegram": f"https://t.me/share/url?url={game_url}&text={game_title}",
        }
        return Response(share_links)
    except NoReverseMatch:
        return Response(
            {
                "error": "Could not resolve URL for the game. Check URL configuration and 'get_absolute_url' method."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

url = "https://afkatservice-a4fegdfndqeddhgw.uaenorth-01.azurewebsites.net/afk_services/"
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_achievments(request: HttpRequest, achievement_id:int):
    endpoint = f"/afk_achievements/{achievement_id}"
    try :

        response  = requests.get(url + endpoint)
        response.raise_for_status()
        return Response(response.json())
    except Exception as e :
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
#
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_game_achievement(request: HttpRequest, game_id:int):
    endpoint = f"/afk_achievements/game/{game_id}"
    try :
        response  = requests.get(url + endpoint)
        response.raise_for_status()
        return Response(response.json())
    except Exception as e :
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
#
#
# @api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
# def post_achievements(request: HttpRequest,):
#     url = f"https://afkatservice-a4fegdfndqeddhgw.uaenorth-01.azurewebsites.net/afk_services/afk_achievements/"
#     try :
#         response  = requests.post(url)
#         response.raise_for_status()
#         return Response(status = HTTP_201_CREATED)
#     except Exception as e :
#         return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
#

class AFKGatewayView(LoginRequiredMixin, View):
    BASE_URL = "https://afkat-f8cfgpgrhkencybn.israelcentral-01.azurewebsites.net"
    # login_url = '/api/v1/auth/login/'

    def dispatch(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return self.handle_no_permission()  .

        forward_path = request.path.replace("/api/v1/games/afk-service", "", 1)

        if not forward_path:
            forward_path = "/"
        elif not forward_path.startswith('/'):
            forward_path = '/' + forward_path

        url = f"{self.BASE_URL}{forward_path}"
        headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

        if 'Authorization' not in headers and request.user.is_authenticated:
            pass

        try:

            headers["Host"] = "afkat-f8cfgpgrhkencybn.israelcentral-01.azurewebsites.net"
            headers.pop("Content-Length", None)
            response = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                data=request.body,
                params=request.GET,
                cookies=request.COOKIES,
                timeout=10,
                allow_redirects=True,
                stream = True,
            )

            django_response = HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.headers.get("Content-Type", "application/json")
            )

            hop_by_hop_headers = {
                'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
                'te', 'trailers', 'transfer-encoding', 'upgrade'
            }

            for header, value in response.headers.items():
                if header.lower() not in hop_by_hop_headers | {'content-length', 'content-encoding'}:
                    django_response[header] = value

            # print("Forwarding to URL:", url)
            # print("Headers:", headers)
            # print("Method:", request.method)
            # print("Params:", request.GET)
            # print("Response status:", response.status_code)
            # print("Response body:", response.text[:500])

            return django_response

        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"error": "AFK service unavailable", "details": str(e)},
                status=502
            )
