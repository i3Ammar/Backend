from django.db.models import Q, Exists, OuterRef
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
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
    queryset = (
        Post.objects.select_related("author", "author__userProfile")
        .prefetch_related("likes")
        .all()
    )
    filterset_class = PostFilterSet
    ordering_fields = ["published_at", "author", "title", "slug"]

    def get_queryset(self):
        queryset = super().get_queryset()

        user_pk = self.kwargs.get("user_pk")
        if user_pk is not None:
            queryset = self.queryset.filter(author__pk = user_pk).order_by("-published_at")

            if self.request.user.is_anonymous:
                queryset = self.queryset.filter(
                    published_at__lte = timezone.now()
                ).order_by("?")

        else:
            if self.request.user.is_anonymous:
                queryset = queryset.filter(published_at__lte = timezone.now()).order_by("?")

            elif not self.request.user.is_staff:
                queryset = queryset.order_by("?")
            else:  # Authenticated
                queryset = queryset.filter(
                    Q(published_at__lte = timezone.now()) | Q(author = self.request.user)
                ).order_by("?")

        if self.request.user.is_authenticated:
            user_likes = Post.likes.through.objects.filter(
                post_id = OuterRef("pk"), user_id = self.request.user.id
            )
            queryset = queryset.annotate(is_liked_by_user = Exists(user_likes))

        return queryset.select_related(
            "author", "author__userProfile"
        ).prefetch_related("likes")

    def list(self, *args, **kwargs):
        return super(PostViewSet, self).list(*args, **kwargs)

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return PostSerializer
        return PostDetailSerializer

    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    @action(methods = ["get"], detail = False, name = "Posts by the logged in user")
    def mine(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to see which Posts are yours")
        posts = (
            self.get_queryset().filter(author = request.user).order_by("-published_at")
        )

        page = self.paginate_queryset(posts)

        if page is not None:
            serializer = PostSerializer(page, many = True, context = {"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many = True, context = {"request": request})
        return Response(serializer.data)

    @action(
        methods = ["get"],
        detail = False,
    )
    def themes(self, request):
        themes = get_available_themes()
        return Response(themes)

    @action(detail = True, methods = ["post"], permission_classes = [IsAuthenticated])
    def like(self, request, pk = None):
        post = self.get_object().prefetch_related("likes")
        user = request.user

        if post.likes.filter(id = user.id).exists():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        return Response(
            {"liked": liked, "likes_count": post.likes.count()},
            status = status.HTTP_200_OK,
        )


@api_view(["GET"])
def get_post_share_links(request, post_pk):
    """Generate social media share links for a post."""
    try:
        post = Post.objects.get(pk = post_pk)

        # Get the absolute URL to the post detail page
        # You'll need to ensure Post has a get_absolute_url method
        post_url = request.build_absolute_uri(post.get_absolute_url())

        # Prepare sharing links for different platforms
        share_links = {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={post_url}",
            "twitter": f"https://twitter.com/intent/tweet?text={post.title}&url={post_url}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={post_url}",
            "reddit": f"https://www.reddit.com/submit?url={post_url}&title={post.title}",
            "email": f"mailto:?subject={post.title}&body=I found this interesting post and thought you might like it: {post_url}",
        }

        return JsonResponse(
            {"post_title": post.title, "post_url": post_url, "share_links": share_links}
        )

    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status = 404)
