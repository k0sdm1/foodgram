from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверяет, является ли пользователь автором объекта."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )
