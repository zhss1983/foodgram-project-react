def get_param_value_serialize(serializer_field, parameter_name, default=None):
    return serializer_field.context['request'].query_params.get(
        parameter_name, default)


def get_param_value_views(view, parameter_name, default=None):
    return view.request.query_params.get(parameter_name, default)


def getlist_param_value_views(view, parameter_name, default=None):
    return view.request.query_params.getlist(parameter_name, default)


class GetQueryParameter():
    """Базовый класс для получения значений по умолчанию"""
    requires_context = True

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    def __call__(self, serializer_field, parameter_name):
        return get_param_value_serialize(serializer_field, parameter_name)


class GetRecipesLimit(GetQueryParameter):
    def __call__(self, serializer_field):
        return get_param_value_serialize(serializer_field, 'recipes_limit', '')
