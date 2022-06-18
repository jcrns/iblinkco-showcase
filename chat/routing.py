# chat/routing.py
from django.urls import re_path

# Importing handler
from .consumers import ChatConsumer

# Specifying routing configuration
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer),
]