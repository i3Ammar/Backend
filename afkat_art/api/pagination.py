from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class GameAndArtLayoutPagination(LimitOffsetPagination):
    default_limit = 24
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
