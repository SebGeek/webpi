from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()), # call the as_asgi() classmethod in order to get an ASGI application that will instantiate an instance of our consumer for each user-connection
]