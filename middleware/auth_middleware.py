# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from django.http import JsonResponse


# class CheckAccessTokenMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Bỏ qua các URL không yêu cầu xác thực
#         if request.path.startswith('/admin/') or request.path.startswith('/api/auth/'):
#             return self.get_response(request)  # Bỏ qua kiểm tra token

#         jwt_auth = JWTAuthentication()
#         try:
#             print(f"Before authentication: {request.user}")  # Có thể là AnonymousUser
#             user_auth_tuple = jwt_auth.authenticate(request)
#             print(f"After authentication: {request.user}")  # Kiểm tra user có được set hay không
#             if user_auth_tuple is None:  # Không có token
#                 return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)

#             request.user, request.auth = user_auth_tuple  # Gán user và token vào request
#             print(f"After authentication2: {request.user}")  # Kiểm tra user có được set hay không
#         except (InvalidToken, TokenError):
#             return JsonResponse({'detail': 'Invalid or expired token'}, status=401)
#         return self.get_response(request)

# from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class CustomAuthMiddleware(MiddlewareMixin):
    ALLOWED_PATHS = [  # Những API không yêu cầu đăng nhập
        "/api/auth/login/",
        "/api/auth/register/",
        "/api/auth/refresh/",
    ]

    def process_request(self, request):
        # Cho phép truy cập các API không cần kiểm tra token
        if request.path in self.ALLOWED_PATHS:
            return None
        
        token = request.headers.get("Authorization")  # Lấy token từ request header
        
        if not token:
            return JsonResponse({"error": "Unauthorized. Token missing."}, status=401)
        
        if token != "your-secret-token":  # Thay thế bằng cách kiểm tra token thực tế
            return JsonResponse({"error": "Invalid token."}, status=401)
        
        return None  # Cho phép request tiếp tục nếu hợp lệ
