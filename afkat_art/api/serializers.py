from rest_framework import serializers
from django.contrib.auth import get_user_model
from afkat_art.models import ArtModel , TagsModel

class ArtSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source = 'creator.username')
    tags = serializers.SlugRelatedField(
        many = True,
        slug_field = "value",
        queryset = TagsModel.objects.all()
    )

    class Meta:
        model = ArtModel
        fields = "__all__"

