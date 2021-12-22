from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from users.models import User

# User = get_user_model()

#class User(AbstractUser):
#    pass

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

    def __str__(self):
        return self.name + ', ' + self.measurement_unit


class Amount(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=1)
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ингредиент'),
        on_delete=models.CASCADE,
        related_name=_('amounts'),
    )
    class Meta:
        verbose_name = _('Количество')
        verbose_name_plural = _('Количество')
        #constraints = (
        #    models.UniqueConstraint(
        #        fields=('amount', 'ingredient'),
        #        name='unique_amount_ingredient',
        #    ),
        #)


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        User,
        verbose_name=_('Автор'),
        on_delete=models.CASCADE,
        related_name=_('recipes')
    )
    name = models.CharField(
        _('Название блюда'),
        max_length=200,
        unique=True
    )
    image = models.ImageField(
        upload_to='Recipe/',
        verbose_name=_('Изображение блюда'),
        blank=True,
        null=True,
        help_text=_('Загрузите изображение. Оптимальный размер 960x339. '
                    'Допускаются 1920x678, 640x226, 480x170 px.'),
    )
    text = models.TextField(_('Текст рецепта'))
    ingredients = models.ManyToManyField(Amount)
    cooking_time = models.IntegerField(default=1)

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        #ordering = ('-pub_date', )
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

    def save(self, *args, **kwargs):
        image = self.image
        if not image:
            return super().save(*args, **kwargs)
        img = Image.open(image)
        if img.width < settings.MIN_WIDTH:
            raise Exception(
                _(
                    f'Ширина изображения меньше {settings.MIN_WIDTH} px, '
                    f'загрузите изображение по меньшей мере {settings.MIN_WIDTH}x'
                    f'{settings.MIN_HEIGHT} px.'
                ),
            )
        if img.height < settings.MIN_HEIGHT:
            raise Exception(
                _(
                    f'Высота изображения меньше {settings.MIN_HEIGHT} px, '
                    f'загрузите изображение по меньшей мере {settings.MIN_WIDTH}x'
                    f'{settings.MIN_HEIGHT} px.'
                ),
            )
        return super().save(*args, **kwargs)

class Selected(models.Model):
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
