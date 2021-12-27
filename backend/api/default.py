class GetDefault:
    """Базовый класс для получения значений по умолчанию"""
    requires_context = True

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class GetRecipesLimit(GetDefault):
    def __call__(self, serializer_field):
        return serializer_field.context['request'].query_params.get('recipes_limit', '')

class GetQueryParameter():
    """Базовый класс для получения значений по умолчанию"""
    requires_context = True

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    def __call__(self, serializer_field, parameter_name):
        return serializer_field.context['request'].query_params.get(parameter_name)

