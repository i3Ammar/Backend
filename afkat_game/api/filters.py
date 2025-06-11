from django_filters import rest_framework as filters
from afkat_game.models import Game
from afkat_art.models import ArtModel

class GameFilter(filters.FilterSet):
    tag = filters.CharFilter(field_name = 'tags__value',lookup_expr = "iexact")

    class Meta:
        model = Game
        fields = ['tag','creator','rating']
class ArtFilter(filters.FilterSet):
    tag = filters.CharFilter(field_name = 'tags__value',lookup_expr = "iexact")

    class Meta:
        model = ArtModel
        fields = ['tags','author','rating']
