import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import chat.routing
import chatbot.routing
from chatbot.middleware import JWTAuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # thêm dòng này để xử lý HTTP
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns +
            chatbot.routing.websocket_urlpatterns
        )
    ),
})
