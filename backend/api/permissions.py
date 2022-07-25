from rest_framework import permissions
from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAuthenticatedOrReadOnly,
)


class IsAdmin(permissions.BasePermission):
    """Даёт разрещение только админу."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_superuser


class EditAccessOrReadOnly(IsAuthenticatedOrReadOnly):
    """Доступ только для чтения или автора или админа."""

    def has_object_permission(self, request, view, obj):
        safe = request.method in SAFE_METHODS
        authorized = (
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or obj.author == request.user)
        )
        return safe or authorized


class RegistrationUserPermission(permissions.BasePermission):
    """Даёт особые права на регистрацию пользователя."""

    def has_permission(self, request, view):
        safe = request.method in SAFE_METHODS
        author = request.user and request.user.is_authenticated
        admin = author and request.user.is_superuser
        return safe or author or admin

    def has_object_permission(self, request, view, obj):
        safe = request.method in SAFE_METHODS
        auth = request.user and request.user.is_authenticated
        author = auth and obj.author == request.user
        admin = auth and request.user.is_superuser
        return safe or author or admin


class AdminOrReadOnly(BasePermission):
    """Доступ только для чтения или для администратора."""

    def has_permission(self, request, view):
        safe = request.method in SAFE_METHODS
        authorized = (
            request.user and request.user.is_authenticated and request.user.is_superuser
        )
        return safe or authorized


class AuthorOrAdminUserPermission(permissions.BasePermission):
    """Даёт особые права на регистрацию пользователя."""

    def has_permission(self, request, view):
        author = request.user and request.user.is_authenticated
        admin = author and request.user.is_superuser
        return author or admin

    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or obj.author == request.user)
        )
