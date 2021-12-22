#from base64 import b64decode, b64encode

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, BasePagination


class LimitPageNumberPagination(PageNumberPagination):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    http://api.example.org/accounts/?page=4
    http://api.example.org/accounts/?page=4&limit=100
    """
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 100
