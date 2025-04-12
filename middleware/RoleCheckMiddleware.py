from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

class RoleCheckMiddleware(MiddlewareMixin):
    # Danh sách API công khai (không yêu cầu đăng nhập)
    PUBLIC_ENDPOINTS = (
        "/api/auth/login/",
        "/api/auth/register/",
        "/api/auth/register-artist/",
        "/api/auth/refresh/",
        "/api/auth/resend-active-link/",
        "/api/trending/playlists/",
        "/api/trending/songs/",
        "/api/trending/albums/",
        "/api/trending/artists/",
        "/api/auth/activate/",
        "/api/auth/login/google/",
        "/api/auth/password-reset/",
        "/api/search/",
        "/api/playlists/songs/",
        "/api/public-profile/",

        #Để ở đây để không dùng middleware này kiểm tra url của chat mà dùng một middleware khác
        "/ws/chat/testroom/",
        "/api/messages/",

        "/api/video/",
    )

    # Quyền truy cập theo role
    ROLE_PERMISSIONS = {
        1: (  # ADMIN
            "/api/admin/",
            "/api/admin/artist-registration-requests/",
            "/api/admin/<str:action>/<int:id>/",
            "/api/admin/accounts/",
            "/api/admin/accounts/<str:action>/<int:id>/",
            "/api/account/",
            "/api/admin/plans/",

          
        ),
        2: (  # ARTIST
            "/api/artist/fetch-artist-collab/",
            "/api/account/",
            "/api/artist/songs/",
            "/api/artist/albums/",
            "/api/artist/song/",
            "/api/artist/create-album/",
            "/api/artist/video/",
            "/api/artist/video/status/",
        ),
        3: (  # USER
            "/api/user/",
            "/api/song/",
            "/api/history/update/",
            "/api/account/",
            "/api/playlists/songs/",
            "/api/plans/",
            "/api/create-payment/",
            "/api/payment-return/",
            "/api/playlist/user/",
            "/api/playlist/create/",
            "/api/playlist/add-song/",
            "/api/search/",
            "/api/public-profile/",
            "/api/public-profile/playlists/",
            "/api/public-profile/albums/",
            "/api/public-profile/popular-songs/",
            "/api/cash-payment/",
            "/api/premium/update/order-playlist/",
            "/api/conversations/user/",
            "/api/conversations/mark-read/",
        ),
    }

    def process_request(self, request):
        # Gán mặc định user là AnonymousUser
        request.user = AnonymousUser()

        # Lấy và xác thực token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                raw_token = auth_header.split(" ", 1)[1]
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(raw_token)
                request.user = jwt_auth.get_user(validated_token)
            except (InvalidToken, TokenError):
                pass  # Giữ request.user là AnonymousUser nếu token lỗi

        # Bỏ qua kiểm tra nếu là endpoint công khai
        print(self._is_public_endpoint(request.path))
        if self._is_public_endpoint(request.path):
            return None

        # Kiểm tra đăng nhập
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        # Lấy role_id từ user
        user_role = getattr(request.user, "role_id", None)


        # Kiểm tra quyền truy cập theo role
        if not self._has_permission(request.path, user_role):
            print("role ",{user_role},"request path ",{request.path},"khong duoc truy cap")
            return JsonResponse({"error": "Forbidden"}, status=403)
        return None

    def _is_public_endpoint(self, path):
        """Kiểm tra xem path có thuộc danh sách công khai không."""
        return any(path.startswith(endpoint) for endpoint in self.PUBLIC_ENDPOINTS)

    def _has_permission(self, path, role):
        """Kiểm tra xem role có quyền truy cập path không."""
        allowed_paths = self.ROLE_PERMISSIONS.get(role, ())
        return any(path.startswith(endpoint) for endpoint in allowed_paths)