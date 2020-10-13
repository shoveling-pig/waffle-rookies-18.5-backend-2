from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    def has_permission(self, request, context):
        return hasattr(request.user, 'participant')

class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, context):
        return hasattr(request.user, 'instructor')