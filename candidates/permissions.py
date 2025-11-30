from rest_framework import permissions

class IsCandidateOwner(permissions.BasePermission):
    """
    Custom permission to only allow candidates to access their own data
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'candidate' and
            hasattr(request.user, 'candidate_profile')
        )
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'candidate'):
            return obj.candidate.user == request.user
        return False