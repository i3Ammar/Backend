from django_filters import rest_framework as filters
from afkat_game.models import Game

class GameFilter(filters.FilterSet):
    tag = filters.CharFilter(field_name = 'tags__value',lookup_expr = "iexact")

    class Meta:
        model = Game
        fields = ['tag','creator','rating']