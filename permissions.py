from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    message = 'permission denied you are not the owner'

    def has_object_permission(self, request, view, obj):
        return obj == request.user