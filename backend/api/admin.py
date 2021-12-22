from django.contrib import admin

from .models import Tag, Follow, Ingredient, Amount, Recipe, Selected
from .forms import TagForm

EMPTY = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ('pk', 'name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    empty_value_display = EMPTY

class SelectedAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = EMPTY


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = EMPTY


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'author', 'name', 'image', 'text')
    search_fields = ('author__username', 'name', 'text')
    empty_value_display = EMPTY


class AmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'amount')
    search_fields = ('ingredient',)
    empty_value_display = EMPTY


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user__username', 'following__username')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Selected, SelectedAdmin)