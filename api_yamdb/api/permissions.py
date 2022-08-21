from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSuperuser(BasePermission):
    """
    Простой permission, проверяющий соответствие пользователей одной
    из двух категорий: админа или суперюзера.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
            or request.user.is_authenticated
            and request.user.is_admin)


class IsAdminOrReadOnly(BasePermission):
    """
    Permission, оставляющий всем кроме пользователей со статусом
    администратора доступными только SAFE METHODS.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin
            or request.method in SAFE_METHODS)


class IsModeratorAdminOrReadOnly(BasePermission):
    """
    Пользователь является суперюзером джанго
    или имеет роль администратора или модератора.
    Просмотр доступен всем пользователям.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_superuser)
