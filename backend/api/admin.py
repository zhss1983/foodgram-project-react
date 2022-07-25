from django.contrib import admin

from .forms import TagForm
from .models import (Amount, Favorite, Follow, Ingredient, Recipe, Tag,
                     TagRecipe, Trolley)

EMPTY = "-пусто-"


class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ("pk", "name", "color", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    empty_value_display = EMPTY


class SelectedAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
    empty_value_display = EMPTY


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    empty_value_display = EMPTY


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "name",
        "image",
        "text",
        "cooking_time",
        "pub_date",
        "in_favorite",
        "get_tags",
    )
    search_fields = ("author__username", "name", "tags__tag__name")
    empty_value_display = EMPTY

    def in_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def get_tags(self, obj):
        names = TagRecipe.objects.filter(recipe=obj).values_list("tag__name", flat=True)
        return ", ".join(names)

    in_favorite.short_description = "Добавлено в избранные, раз"
    get_tags.short_description = "Тэги"


class AmountAdmin(admin.ModelAdmin):
    list_display = ("pk", "ingredient", "amount", "recipe")
    search_fields = ("ingredient",)
    empty_value_display = EMPTY


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "tag", "recipe")
    search_fields = ("tag__name", "recipe__name")
    empty_value_display = EMPTY


class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    search_fields = ("user__username", "author__username")


class TrolleyAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user__username", "recipe__name")


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favorite, SelectedAdmin)
admin.site.register(Trolley, TrolleyAdmin)
