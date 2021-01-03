# https://channels.readthedocs.io/en/stable/tutorial/part_2.html

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .views import unicolor, stop_music, set_volume, continue_music, play_music
import ledstrip.glob_var
from ledstrip.forms import blind_music_choices


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
        context = {'team': text_data_json['team']}

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
        context = {}

        if text_data_json['team'] in ['blue', 'red']:
            if ledstrip.glob_var.faster_team_to_answer == None:
                ledstrip.glob_var.faster_team_to_answer = text_data_json['team']
                if text_data_json['team'] == 'blue':
                    rgb_color = ledstrip.glob_var.blue
                else:
                    rgb_color = ledstrip.glob_var.red
                stop_music()
                unicolor(rgb_color)

        elif text_data_json['team'] == 'master':
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

            if text_data_json['blind_music'] == 'off':
                stop_music()
            elif text_data_json['blind_music'] != '':
                ledstrip.glob_var.faster_team_to_answer = None
                unicolor(ledstrip.glob_var.white)
                play_music(text_data_json['blind_music'])

            if text_data_json['volume'] != None:
                set_volume(text_data_json['volume'])

            if text_data_json['bad_answer_continue'] == True:
                ledstrip.glob_var.faster_team_to_answer = None
                unicolor(ledstrip.glob_var.white)
                continue_music()

            context.update({'blind_music_choices': blind_music_choices})

        context.update({'team': text_data_json['team'], 'faster_team_to_answer': ledstrip.glob_var.faster_team_to_answer,
                        'blue_score': ledstrip.glob_var.blue_score, 'red_score': ledstrip.glob_var.red_score})

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