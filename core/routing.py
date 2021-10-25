from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path

from web.consumers import WSConsumer
from sorteo.consumers import SorteoWSConsumer
from sync.consumers import SyncWSConsumer
from chat.consumers import ChatConsumer

application = ProtocolTypeRouter({   
    "websocket": AuthMiddlewareStack(
        URLRouter([          
            path('ws/web/', WSConsumer.as_asgi()),
            path('ws/sync/', SyncWSConsumer.as_asgi()),
            re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
            re_path(r'ws/sorteo/(?P<room_name>\w+)/$', SorteoWSConsumer.as_asgi()),
        ]),
    ),
})




