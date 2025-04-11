import os

# Đặt biến môi trường settings sớm
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotifyCloneBackend.settings')

# Gọi django.setup() trước khi import Django-related modules
import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# Sau setup mới được import middleware hoặc model
from middleware.MiddleWareChat import JWTAuthMiddleware
import api.urls

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            api.urls.websocket_urlpatterns
        )
    ),
})
