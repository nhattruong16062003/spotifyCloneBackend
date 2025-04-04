from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Chỉ cho phép người dùng có quyền admin truy cập vào API này.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == "admin"


class IsArtist(BasePermission):
    """
    Chỉ cho phép người dùng là nghệ sĩ truy cập vào API này.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == "artist"


# class IsAuthenticated(BasePermission):
#     """
#     Chỉ cho phép người dùng đã đăng nhập truy cập vào API này.
#     """
#     def has_permission(self, request, view):
#         return request.user.is_authenticated
