from datetime import timedelta

from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from afkat_auth.permissions import UserIsOwnerOrReadOnly
from afkat_home.api.filters import PostFilterSet
from afkat_home.api.serializers import (
    PostSerializer,
    PostDetailSerializer,
)
from afkat_home.models import Post
from afkat_home.utils import get_available_themes

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [UserIsOwnerOrReadOnly | IsAdminUser]
    queryset = Post.objects.all()
    filterset_class = PostFilterSet
    ordering_fields = ["published_at", "author", "title", "slug"]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            queryset = self.queryset.filter(published_at__lte=timezone.now())

        elif not self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(
                Q(published_at__lte=timezone.now()) | Q(author=self.request.user)
            )

        user_pk = self.kwargs.get('pk')
        if user_pk is not None:
            queryset = self.queryset.filter(author__pk=user_pk)

        return queryset

    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    @method_decorator(cache_page(2 * 60))
    def list(self, *args, **kwargs):
        return super(PostViewSet, self).list(*args, **kwargs)

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return PostSerializer
        return PostDetailSerializer

    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    @action(methods=["get"], detail=False, name="Posts by the logged in user")
    def mine(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to see which Posts are yours")
        posts = self.get_queryset().filter(author=request.user)

        page = self.paginate_queryset(posts)

        if page is not None:
            serializer = PostSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @action(methods=["get"], detail=False, )
    def themes(self, request):
        themes = get_available_themes()
        return Response(themes)

