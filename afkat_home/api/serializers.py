from rest_framework import serializers

from afkat_auth.models import User
from afkat_home.models import Comment, Post, Tag


class TagField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(value=data.lower())[0]
        except (TypeError, ValueError):
            self.fail(f"Tag value {data} is invalid")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    profile_url = serializers.HyperlinkedIdentityField(
        view_name="api_user_detail",
    )

    class Meta:
        model = User
        fields = ["username", "profile_url"]

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    creator = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "creator", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]




class PostSerializer(serializers.ModelSerializer):
    tags = TagField(slug_field="value", many=True, queryset=Tag.objects.all())
    author = AuthorSerializer(read_only=True)


    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["slug","modified_at", "created_at"]


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True) # need to be checked

    # @permission_classes(UserIsOwnerOrReadOnly | IsAdminUser )
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
