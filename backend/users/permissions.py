from rest_framework import permissions

from .constants import ADMIN


class IsAdmin(permissions.BasePermission):
    """Даёт разрещение аутентифицированному пользователю
    со статусом админа.
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and ((request.user.role == ADMIN)
                     or request.user.is_superuser))
