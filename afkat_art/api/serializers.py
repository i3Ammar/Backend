from rest_framework import serializers
from afkat_art.models import ArtModel , TagsModel

class ArtSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source = 'author.username')
    tags = serializers.SlugRelatedField(
        many = True,
        slug_field = "value",
        queryset = TagsModel.objects.all()
    )
    user_id = serializers.ReadOnlyField(source = 'author.id')

    class Meta:
        model = ArtModel
        fields = "__all__"

    # def validate (self ,)
