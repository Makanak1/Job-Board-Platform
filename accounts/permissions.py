from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allow access only to admin users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'admin'

class IsEmployerOrReadOnly(permissions.BasePermission):
    """
    Allow employers to edit, others to read only
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.user_type == 'employer'

class IsCandidateOrReadOnly(permissions.BasePermission):
    """
    Allow candidates to edit, others to read only
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.user_type == 'candidate'