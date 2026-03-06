from rest_framework.permissions import BasePermission


class IsBorrowerOrAdmin(BasePermission):
    """
    Allows access if the user owns the borrow record or is staff.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated) and (
            request.user.is_staff or obj.user_id == request.user.id
        )
