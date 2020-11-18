from rest_framework import permissions

class IsParticipant(permissions.BasePermission):

    def has_permission(self, request):
        return hasattr(request.user, 'participant')

    def has_permission(self, request):
        return hasattr(request.user, 'instructor')