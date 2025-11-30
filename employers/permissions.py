from rest_framework import permissions

class IsEmployerOwner(permissions.BasePermission):
    """
    Custom permission to only allow employers to access their own data
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'employer' and
            hasattr(request.user, 'employer_profile')
        )
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user