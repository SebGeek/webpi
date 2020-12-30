from django.urls import re_path

from . import consumers

# call the as_asgi() classmethod in order to get an ASGI application that will instantiate an instance of our consumer for each user-connection
websocket_urlpatterns = [
    re_path(r'ws/team_blind/$', consumers.ChatConsumer.as_asgi()),
]