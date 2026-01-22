from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Allows access only to admin users
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )



class IsAdminOrReadOnly(BasePermission):
    """
    Admin: full access
    Others: read-only
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )

class IsOwnerOrReadOnly(BasePermission):
    """
    - Property owner can CREATE, UPDATE, DELETE their own property
    - Admin can do everything
    - Buyer can READ only
    """

    def has_permission(self, request, view):
        """CREATE: only property owner"""
        if request.method == 'POST':
            return (
                request.user.is_authenticated and
                request.user.role == 'property_owner'
            )

        """UPDATE / DELETE: checked at object level"""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Everyone can READ"""
        if request.method in SAFE_METHODS:
            return True

        """Admin can do anything"""
        if request.user.role == 'admin':
            return True

        """Property owner can modify ONLY their own property"""
        return (
            request.user.role == 'owner' and
            obj.owner == request.user
        )