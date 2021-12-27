from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        _('Имя тега'),
        max_length=200,
        unique=True
    )
    color = models.CharField(
        _('Цвет тега'),
        max_length=7,
        null=True,
        blank=True
    )
    slug = models.SlugField(
        _('Адрес тега'),
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        _('Название ингредиента'),
        max_length=200,
    )
    measurement_unit = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        unique_together = ('name', 'measurement_unit',)
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
#    tags = models.ManyToManyField(
#        Tag,
#        verbose_name=_('Тэги'),
#        #related_name=_('recipes'),
##        blank=False,
##        null=False
#    )
    author = models.ForeignKey(
        User,
        verbose_name=_('Автор'),
        on_delete=models.CASCADE,
        related_name=_('recipes'),
        blank=False,
        null=False
    )
    name = models.CharField(
        _('Название блюда'),
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    image = models.ImageField(
        upload_to=_('Recipe/'),
        verbose_name=_('Изображение блюда'),
        blank=True,
        null=True,
        help_text=_('Загрузите изображение. Оптимальный размер xxx*yyy px.'),
    )
    text = models.TextField(
        verbose_name=_('Текст рецепта'),
        blank=False,
        null=False
    )
    #ingredients = models.ManyToManyField(
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
    #)
    cooking_time = models.IntegerField(
        verbose_name=_('Время приготовления'),
        default=1
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('name', )  # ('-pk', )
        constraints = (
            models.CheckConstraint(
                check=Q(cooking_time__gte=1),
                name='cooking_time_more_or_equal_minute',
            ),
        )

    def __str__(self):
        return self.name[:25]

    def delete(self, *args, **kwargs):
        self.image.delete()
        return super().delete(*args, **kwargs)

#    def save(self, *args, force_insert=False, force_update=False, using=None,
#             update_fields=None, **kwargs):
#        if not force_insert and (
#                force_update or update_fields) and ('image' in update_fields):
#            print(settings.MEDIA_ROOT / self.image.upload_to / self.image.path)
#            self.image.delete()
#        return super().save(*args, **kwargs)

#    def save(self, *args, **kwargs):
#        return super().save(*args, **kwargs)


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

    def __str__(self):
        return f'{self.ingredient.name}, {self.amount} {self.ingredient.measurement_unit}'

    class Meta:
        verbose_name = _('Количество')
        verbose_name_plural = _('Количество')
        ordering = ('recipe__name', 'ingredient__name', )
        constraints = (
#            models.UniqueConstraint(
#                fields=('amount', 'ingredient'),
#                name='unique_amount_ingredient',
#            ),
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name='amount_positive',
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
        ordering = ('user__username', 'recipe__name', )


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
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        ordering = ('user__username', 'author__username')
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='name_not_author',
            )
        )
