from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    from rest_framework_simplejwt.tokens import AccessToken
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']  # Lấy user_id từ payload JWT
        return User.objects.get(id=user_id)
    except Exception as e:
        print(f"Invalid token: {e}")
        return AnonymousUser()

class JWTAuthMiddleware:
    # Danh sách URL cần xác thực token
    AUTH_REQUIRED_PATHS = [
        "/ws/chat/",  # Chỉ xác thực cho ws/chat/
    ]

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Lấy path từ scope
        path = scope.get("path", "")

        # Nếu path không nằm trong danh sách cần xác thực, bỏ qua middleware
        if not any(path.startswith(p) for p in self.AUTH_REQUIRED_PATHS):
            return await self.inner(scope, receive, send)

        # Lấy token từ query string
        query_string = scope["query_string"].decode()
        query_params = dict(qp.split("=") for qp in query_string.split("&") if qp)
        token = query_params.get("token")

        if not token:
            await send({
                "type": "websocket.close",
                "code": 1008,
                "reason": "No token provided",
            })
            return

        # Xác thực token và lấy user
        user = await get_user_from_token(token)
        if isinstance(user, AnonymousUser):
            await send({
                "type": "websocket.close",
                "code": 1008,
                "reason": "Invalid or expired token",
            })
            return

        # Gán user vào scope
        scope["user"] = user

        # Chuyển tiếp đến consumer
        return await self.inner(scope, receive, send)