from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return bool(obj.author == request.user or request.user.is_staff)