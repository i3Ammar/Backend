from django.http import FileResponse
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from afkat_art.api.serializers import ArtSerializer, ArtRatingSerializer, ArtCommentSerializer
from afkat_game.api.filters import ArtFilter
from .pagination import GameAndArtLayoutPagination
from ..models import ArtModel, ArtRating, ArtComment
from ..services.art_services import validate_art_file


class ArtViewSet(viewsets.ModelViewSet):
    queryset = ArtModel.objects.all().select_related("author").prefetch_related("tags")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ArtSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = ArtFilter
    pagination_class = GameAndArtLayoutPagination
    search_fields = ["title__icontains"]

    def perform_create(self, serializer):
        validate_art_file(self, serializer.validated_data["model_file"])
        serializer.save(author = self.request.user)

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You dont have permission to delete this ArtModle.")

    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



    @action(detail = True, methods = ["post"], permission_classes = [permissions.IsAuthenticated])
    def comment(self, request, pk = None):
        art = self.get_object()
        serializer = ArtCommentSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save(user = request.user, art = art)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail = True, methods = ["get"], permission_classes = [permissions.IsAuthenticated])
    def comments(self, request, pk = None):
        art = self.get_object()
        comments = ArtComment.objects.filter(art = art).select_related('user','art')
        serializer = ArtCommentSerializer(comments, many = True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        art = self.get_object()

        try:
            rating = ArtRating.objects.get(user=request.user, art=art)
            serializer = ArtRatingSerializer(rating, data=request.data)
        except ArtRating.DoesNotExist:
            serializer = ArtRatingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, art=art)
            art.refresh_from_db()
            return Response({"rating": serializer.data, "art_avg_rating": art.rating})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods = ["get"], detail = True, url_path = "download")
    def download_art(self, request, pk = None):
        art = get_object_or_404(ArtModel, pk = pk)
        art.download_count += F("download_count")+1
        art.save(update_fields = ["download_count"])
        response = FileResponse(
            art.model_file.open("rb"), as_attachment = True, filename = art.model_file.name
        )
        return response


class ArtCommentViewSet(viewsets.ModelViewSet):
    queryset = ArtComment.objects.all().select_related('user', 'art')
    serializer_class = ArtCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


