from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from users.models import User


class Tag(models.Model):
    """Модель содержит представление о тегах рецептов."""

    name = models.CharField(verbose_name=_("Имя тега"), max_length=200, unique=True)
    color = models.CharField(
        verbose_name=_("Цвет тега"),
        max_length=7,
    )
    slug = models.SlugField(verbose_name=_("Адрес тега"), unique=True)

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ "Модель содержит представление всех ингредиентов."""

    name = models.CharField(
        verbose_name=_("Название ингредиента"),
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name=_("Единица измерения"),
        max_length=50,
    )

    class Meta:
        verbose_name = _("Ингредиент")
        verbose_name_plural = _("Ингредиенты")
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name=_("Ingredient_unique_name_and_measurement_unit"),
            ),
        )

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    """Модель содержит представление всех рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name=_("Автор"),
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=200,
    )
    image = models.ImageField(
        upload_to=_("Recipe/"),
        verbose_name=_("Картинка"),
        help_text=_("Загрузите изображение"),
    )
    text = models.TextField(
        verbose_name=_("Текстовое описание"),
    )
    cooking_time = models.IntegerField(
        verbose_name=_("Время приготовления, мин"),
        default=1,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата публикации"),
    )

    class Meta:
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")
        ordering = ("-pk",)
        constraints = (
            models.CheckConstraint(
                check=Q(cooking_time__gte=1),
                name=_("cooking_time_more_or_equal_minute"),
            ),
        )

    def __str__(self):
        return self.name[:25]

    def delete(self, *args, **kwargs):
        self.image.delete()
        return super().delete(*args, **kwargs)


class TagRecipe(models.Model):
    """Модель связывает тэги с рецептами."""

    tag = models.ForeignKey(
        Tag,
        verbose_name=_("Тэги"),
        on_delete=models.CASCADE,
        related_name="tag_recipes",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_("Рецепт"),
        on_delete=models.CASCADE,
        related_name="tags",
    )

    class Meta:
        verbose_name = _("Тэг рецепта")
        verbose_name_plural = _("Тэги рецептов")
        ordering = (
            "recipe__name",
            "tag__name",
        )
        constraints = (
            models.UniqueConstraint(
                fields=("tag", "recipe"),
                name=_("unique_tag_recipe_pair"),
            ),
        )

    def __str__(self):
        return f"{self.id}: {self.recipe.name}, {self.tag.name}"


class Amount(models.Model):
    """Модель связывает рецепты с ингредиентами и их количеством."""

    amount = models.DecimalField(
        verbose_name=_("Количество"),
        max_digits=7,
        decimal_places=2,
        default=1,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_("Ингредиент"),
        on_delete=models.CASCADE,
        related_name=_("amounts"),
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_("Рецепт"),
        on_delete=models.CASCADE,
        related_name=_("ingredients"),
    )

    class Meta:
        verbose_name = _("Количество")
        verbose_name_plural = _("Количество")
        ordering = ("recipe__name", "ingredient__name")
        constraints = (
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name=_("amount_positive"),
            ),
        )

    def __str__(self):
        return (
            f"{self.ingredient.name}, {self.amount} "
            f"{self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """Модель связывает пользователей и их любимые рецепты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="selecter",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_("Рецепт"),
        related_name="selected",
    )

    class Meta:
        verbose_name = _("Избранный рецепт")
        verbose_name_plural = _("Избранные рецепты")
        ordering = ("user__username", "recipe__name")
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name=_("Favorite_unique_user_recipe_pair"),
            ),
        )

    def __str__(self):
        return f"{self.user} -> {self.recipe}"


class Follow(models.Model):
    """Модель связывает пользователей и избранных авторов рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Автор"),
        related_name="following",
    )

    class Meta:
        verbose_name = _("Подписка на автора")
        verbose_name_plural = _("Подписки на авторов")
        ordering = ("user__username", "author__username")
        constraints = (
            models.UniqueConstraint(
                fields=("user", "author"),
                name=_("Follow_unique_user_author"),
            ),
            models.CheckConstraint(
                check=~Q(user=F("author")),
                name=_("name_not_author"),
            ),
        )

    def __str__(self):
        return f"{self.user} -> {self.author}"


class Trolley(models.Model):
    """Модель связывает пользователя с выбранными им рецептами."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="trolley",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_("Рецепт"),
        related_name="trolley",
    )

    class Meta:
        verbose_name = _("Корзина")
        verbose_name_plural = _("Корзины")
        ordering = ("user__username", "recipe__name")
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name=_("Trolley_unique_user_recipe_pair"),
            ),
        )

    def __str__(self):
        return f"{self.pk}: {self.user}, {self.recipe}"
