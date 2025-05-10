from rest_framework import serializers

from afkat.utils.serializer_field import CompressedImageField
from afkat_auth.models import User
from afkat_home.models import Comment, Post

class AuthorSerializer(serializers.ModelSerializer):
    profile_url = serializers.HyperlinkedIdentityField(
        view_name="api_user_detail",
    )

    class Meta:
        model = User
        fields = ["username", "profile_url"]
        extra_kwargs = {
            'username': { 'required':False}
        }

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    creator = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "creator", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]




class PostSerializer(serializers.ModelSerializer):
    # author = AuthorSerializer(read_only=True)
    username = serializers.ReadOnlyField(source = 'author.username')
    user_id = serializers.ReadOnlyField(source = 'author.id')
    user_profile_image = serializers.URLField(source='author.userProfile.profile_image.url',read_only = True)


    image = CompressedImageField(
        max_size=1200,
        quality=80,
        maintain_format=True,
        max_file_size_kb=500
    )
    class Meta:
        model = Post
        exclude = ["author"]
        read_only_fields = ["slug","modified_at", "created_at"]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)



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
