from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        _('Имя тега'),
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    color = models.CharField(
        _('Цвет тега'),
        max_length=7,
        blank=False,
        null=False
    )
    slug = models.SlugField(
        verbose_name=_('Адрес тега'),
        unique=True,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('name', )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_('Название ингредиента'),
        max_length=200,
        blank=False,
        null=False
    )
    measurement_unit = models.CharField(
        max_length=50,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        unique_together = ('name', 'measurement_unit')
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name=_('Автор'),
        on_delete=models.CASCADE,
        related_name=_('recipes'),
        blank=False,
        null=False
    )
    name = models.CharField(
        _('Название'),
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    image = models.ImageField(
        upload_to=_('Recipe/'),
        verbose_name=_('Картинка'),
        help_text=_('Загрузите изображение'),
        blank=False,
        null=False
    )
    text = models.TextField(
        verbose_name=_('Текстовое описание'),
        blank=False,
        null=False
    )
    cooking_time = models.IntegerField(
        verbose_name=_('Время приготовления, мин'),
        default=1,
        blank=False,
        null=False
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата публикации'),
    )

    #  tags = models.ManyToManyField(
    #    Tag,
    #    verbose_name=_('Тэги'),
    #    #related_name=_('recipes'),
    #    #blank=False,
    #    #null=False
    #  )

    #  ingredients = models.ManyToManyField(
    #    Ingredient,
    #    through='Amount',
    #    #related_name=_('ingredients'),
    #    verbose_name=_('Ингредиенты'),
    #    #related_query_name=None,
    #    #limit_choices_to=None,
    #    #symmetrical=None,
    #    through_fields=('recipe', 'ingredient'),
    #    #db_constraint=True,
    #    #db_table=None,
    #    #swappable=True
    #  )

    #  При ужарки и уварки происходит изменение массы, надо предусмотреть поле
    #  для заполнения данного параметра. Задел на будущее.
    #    food_yield = models.DecimalField(
    #        verbose_name=_('Размер порции'),
    #        max_digits=7,
    #        decimal_places=2,
    #        default=1,
    #        blank=False,
    #        null=False
    #    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-pk', )
        constraints = (
            models.CheckConstraint(
                check=Q(cooking_time__gte=1),
                name=_('cooking_time_more_or_equal_minute'),
            ),
        )

    def __str__(self):
        return self.name[:25]

    def delete(self, *args, **kwargs):
        self.image.delete()
        return super().delete(*args, **kwargs)


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name=_('Тэги'),
        on_delete=models.CASCADE,
        related_name=_('tagrecipes'),
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('Рецепт'),
        on_delete=models.CASCADE,
        related_name=_('tags'),
    )

    def __str__(self):
        return f'{self.id}: {self.recipe.name}, {self.tag.name}'

    class Meta:
        verbose_name = _('Тэг рецепта')
        verbose_name_plural = _('Тэги рецептов')
        ordering = ('recipe__name', 'tag__name', )
        constraints = (
            models.UniqueConstraint(
                fields=('tag', 'recipe'),
                name=_('unique_tag_recipe_pair'),
            ),
        )


class Amount(models.Model):
    amount = models.DecimalField(
        verbose_name=_('Количество'),
        max_digits=7,
        decimal_places=2,
        default=1,
        blank=False,
        null=False
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ингредиент'),
        on_delete=models.CASCADE,
        related_name=_('amounts'),
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('Рецепт'),
        on_delete=models.CASCADE,
        related_name=_('ingredients'),
    )
    # Количество порций. Из-за того что стандартной массы с рецепта может быть
    # слишком мало или много пользователь может приготовить другой объём.
    # Множитель для рецепта в корзине. Заготовка на будущее.
#    portions = models.DecimalField(
#        verbose_name=_('Количество порций'),
#        max_digits=7,
#        decimal_places=2,
#        default=1,
#        blank=False,
#        null=False
#    )

    def __str__(self):
        return (f'{self.ingredient.name}, {self.amount} '
                f'{self.ingredient.measurement_unit}')

    class Meta:
        verbose_name = _('Количество')
        verbose_name_plural = _('Количество')
        ordering = ('recipe__name', 'ingredient__name')
        constraints = (
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name=_('amount_positive'),
            ),
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='selecter',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        related_name='selected',
    )

    class Meta:
        verbose_name = _('Избранный рецепт')
        verbose_name_plural = _('Избранные рецепты')
        ordering = ('user__username', 'recipe__name')
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=_('Favorite_unique_user_recipe_pair'),
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор'),
        related_name='following',
    )

    class Meta:
        verbose_name = _('Подписка на автора')
        verbose_name_plural = _('Подписки на авторов')
        ordering = ('user__username', 'author__username')
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name=_('Follow_unique_user_author'),
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name=_('name_not_author'),
            )
        )

    def __str__(self):
        return f'{self.user} -> {self.author}'


class Trolley(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='trolley')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='trolley')

    class Meta:
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзины')
        ordering = ('user__username', 'recipe__name')
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=_('Trolley_unique_user_recipe_pair'),
            ),
        )

    def __str__(self):
        return f'{self.pk}: {self.user}, {self.recipe}'
