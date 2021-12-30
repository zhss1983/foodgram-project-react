from rest_framework.filters import SearchFilter


class NameSearchFilter(SearchFilter):
    search_param = 'name'
