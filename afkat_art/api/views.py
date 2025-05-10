from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import  PermissionDenied
from rest_framework.response import Response

import afkat_art
from afkat_art.api.serializers import ArtSerializer
from .pagination import GameAndArtLayoutPagination
from ..models import ArtModel
from ..services.art_services import validate_art_file


class ArtViewSet (viewsets.ModelViewSet):
    queryset = ArtModel.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ArtSerializer
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    pagination_class = GameAndArtLayoutPagination
    search_fields = ['title__icontains']


    def perform_create(self, serializer):
        validate_art_file(self, serializer.validated_data['model_file'])
        serializer.save(author = self.request.user)

    def perform_destroy(self, instance):
        if instance.creator == self.request.user:
            instance.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You dont have permission to delete this Game.")

    @method_decorator(vary_on_headers('Authorization','Cookie'))
    @method_decorator(cache_page(60 * 10))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(vary_on_headers('Authorization','Cookie'))
    @method_decorator(cache_page(60 * 5))
    def list(self , request , *args , **kwargs):
        return super().list(request , *args , **kwargs)


    @action(methods = ["get"], detail = True, url_path = "download")
    def download_game(self, request, pk = None):
        art = get_object_or_404(ArtModel, pk = pk)
        art.download_count += 1
        art.save(update_fields = ["download_count"])
        response = FileResponse(
            art.model_file.open("rb"), as_attachment = True, filename = art.model_file.name
        )
        return response
