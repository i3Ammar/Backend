from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class GameAndArtLayoutPagination(PageNumberPagination, LimitOffsetPagination):
    default_limit = 2
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
