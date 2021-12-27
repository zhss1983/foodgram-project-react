from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import ACCESS_LEVEL, ADMIN, USER
from .managers import CustomUserManager


class User(AbstractUser):
    """Кастомная модель пользователя с доплнительным полм 'role', first_name, last_name, email."""

    role = models.CharField(
        verbose_name='Права',
        max_length=9,
        choices=ACCESS_LEVEL,
        default=USER
    )
    #first_name = models.CharField(_('first name'), max_length=150, blank=False)
    #last_name = models.CharField(_('last name'), max_length=150, blank=False)
    #email = models.EmailField(_('email address'), unique=False)
    AbstractUser.first_name.max_length = 150
    AbstractUser.last_name.max_length = 150
    # Необходимо для того, чтобы при создании
    # пользователя через консоль, запрашивался
    # email
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name',]
    #REQUIRED_FIELDS = ['username', 'first_name', 'last_name',]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    @property
    def not_admin(self):
        return self.role != ADMIN

    def __str__(self):
        return self.username
