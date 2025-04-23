from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets, status, filters
from rest_framework.exceptions import  PermissionDenied

import afkat_art
from afkat_art.api.serializers import ArtSerializer
from .pagination import GameAndArtLayoutPagination
from ..models import ArtModel


class ArtViewSet (viewsets.ModelViewSet):
    queryset = ArtModel.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ArtSerializer
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    pagination_class = GameAndArtLayoutPagination
    search_fields = ['title']

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def list(self , request , *args , **kwargs):
        return super().list(request , *args , **kwargs)
