from django.contrib.auth.base_user import BaseUserManager

from .constants import ADMIN


class CustomUserManager(BaseUserManager):
    """
    В методе create_superuser() присваиваем
    дефолное значение поля 'role' = 'admin'.
    """
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', ADMIN)
        return self.create_user(email, password, **extra_fields)
