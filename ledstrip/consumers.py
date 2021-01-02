# https://channels.readthedocs.io/en/stable/tutorial/part_2.html

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .views import unicolor, stop_music
import ledstrip.glob_var


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat'

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
                   'blue_score': ledstrip.glob_var.blue_score, 'red_score': ledstrip.glob_var.red_score}

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

class TeamBlindConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'team_blind'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if text_data_json['team'] in ['blue', 'red']:
            print(f"{text_data_json['team']}")
        elif text_data_json['team'] == 'master':
            print(f"master {text_data_json}")
            if text_data_json['add_point'] == 'blue':
                ledstrip.glob_var.blue_score += 1
                unicolor(ledstrip.glob_var.white)
            elif text_data_json['add_point'] == 'red':
                ledstrip.glob_var.red_score += 1
                unicolor(ledstrip.glob_var.white)
            if text_data_json['remove_point'] == 'blue':
                ledstrip.glob_var.blue_score -= 1
            elif text_data_json['remove_point'] == 'red':
                ledstrip.glob_var.red_score -= 1
            elif text_data_json['remove_point'] == 'reset':
                ledstrip.glob_var.blue_score = 0
                ledstrip.glob_var.red_score = 0

        context = {'team': text_data_json['team'], 'faster_team_to_answer': ledstrip.glob_var.faster_team_to_answer,
                   'blue_score': ledstrip.glob_var.blue_score, 'red_score': ledstrip.glob_var.red_score}

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'blind_message',
                'context': context
            }
        )

    # Receive message from room group
    async def blind_message(self, event):
        context = event['context']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'context': context}))