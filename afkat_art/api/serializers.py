from rest_framework import serializers

from afkat.utils.serializer_field import CompressedImageField
from afkat_art.models import ArtModel , TagsModel

class ArtSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source = 'author.username')
    tags = serializers.SlugRelatedField(
        many = True,
        slug_field = "value",
        queryset = TagsModel.objects.all()
    )
    user_id = serializers.ReadOnlyField(source = 'author.id')

    thumbnail = CompressedImageField(
        max_size=1200,
        quality=80,
        maintain_format=True,
        max_file_size_kb=500
    )
    class Meta:
        model = ArtModel
        fields = "__all__"
        read_only_fields = ["download_count"]

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        art = ArtModel.objects.create(**validated_data)
        art.tags.set(tags_data)
        return art
