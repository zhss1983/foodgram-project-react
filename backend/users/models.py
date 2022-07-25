from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):
    AbstractUser.first_name.max_length = 150
    AbstractUser.last_name.max_length = 150

    REQUIRED_FIELDS = (
        "email",
        "first_name",
        "last_name",
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.username
