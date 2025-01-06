from rest_framework.permissions import BasePermission


class IsClienteUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_cliente)


class IsFundacionUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_fundacion)
