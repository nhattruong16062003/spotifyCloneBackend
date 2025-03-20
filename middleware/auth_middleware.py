from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.http import JsonResponse

class CheckAccessTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bỏ qua các URL không yêu cầu xác thực
        if request.path.startswith('/api/auth/'):
            return self.get_response(request)

        jwt_auth = JWTAuthentication()
        try:
            # Xác thực token
            jwt_auth.authenticate(request)
        except (InvalidToken, TokenError):
            return JsonResponse({'detail': 'Invalid or expired token'}, status=401)

        return self.get_response(request)