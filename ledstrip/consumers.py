# https://channels.readthedocs.io/en/stable/tutorial/part_2.html

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .views import unicolor, stop_music
import ledstrip.glob_var


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'team_blind'
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = f"{text_data_json['team']} team: {text_data_json['message']}"

        if text_data_json['team'] in ['blue', 'red']:
            ledstrip.glob_var.faster_team_to_answer = text_data_json['team']
            if text_data_json['team'] == 'blue':
                rgb_color = ledstrip.glob_var.blue
            else:
                rgb_color = ledstrip.glob_var.red
            stop_music()
            unicolor(rgb_color)

        context = {'team': text_data_json['team'], 'faster_team_to_answer': ledstrip.glob_var.faster_team_to_answer,
                   'blue_score': ledstrip.glob_var.blue_score, 'red_score': ledstrip.glob_var.red_score, 'room_name': 'team_blind'}

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'context': context
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        context = event['context']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'context': context
        }))