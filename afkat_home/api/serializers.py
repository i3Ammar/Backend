from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser

from afkat.utils.serializer_field import CompressedImageField
from afkat_auth.models import (
    User,
)
from afkat_auth.permissions import UserIsOwnerOrReadOnly
from afkat_home.models import Comment, Post

AuthUser = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    profile_url = serializers.HyperlinkedIdentityField(
        view_name = "api_user_detail",
    )

    class Meta:
        model = User
        fields = ["username", "profile_url"]
        extra_kwargs = {"username": {"required": False}}


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required = True)
    creator = AuthorSerializer(read_only = True)

    class Meta:
        model = Comment
        fields = ["id", "creator", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    # author = AuthorSerializer(read_only=True)
    username = serializers.ReadOnlyField(source = "author.username")
    user_id = serializers.ReadOnlyField(source = "author.id")
    user_profile_image = serializers.URLField(
        source = "author.userProfile.profile_image.url", read_only = True
    )
    user_is_following = serializers.BooleanField(source = "author.is_following ", read_only = True)
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.BooleanField(read_only = True, default = False)

    image = CompressedImageField(
        max_size = 1200,
        quality = 80,
        maintain_format = True,
        max_file_size_kb = 500,
        required = False,
        allow_null = True,
    )

    class Meta:
        model = Post
        exclude = ["author", "likes"]
        read_only_fields = ["slug", "modified_at", "created_at", "likes_count"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked_by_user(self, obj):
        user = self.context["request"].user
        if user and user.is_authenticated:
            return obj.likes.filter(id = user.id).exists()
        return False

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many = True)  # need to be checked

    @permission_classes(UserIsOwnerOrReadOnly | IsAdminUser)
    def update(self, instance, validated_data):
        comments = validated_data.pop("comments")
        instance = super(PostDetailSerializer, self).update(instance, validated_data)

        for comment_data in comments:
            if comment_data.get("id"):
                continue
            comment = Comment(**comment_data)
            comment.creator = self.context["request"].user
            comment.content_object = instance
            comment.save()
        return instance
