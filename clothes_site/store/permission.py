from rest_framework import permissions


class CheckOwnerOrder(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.order_user:
            return True
        return False