import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Spot


COORDS = {}


class CoordRecord:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


@database_sync_to_async
def create_spot_record(y, x, channel_name):
    Spot.objects.update_or_create(
        defaults={'y': y, 'x': x}, channel_name=channel_name)
    print(Spot.objects.all())


@database_sync_to_async
def delete_spot_record(channel_name):
    print('in delete')
    print(Spot.objects.filter(channel_name=channel_name))
    Spot.objects.filter(channel_name=channel_name).delete()


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        super().__init__()
        self.chats = []

    async def connect(self):
        # self.room_name = (
        #     f'{self.scope["url_route"]["kwargs"]["y"]}'
        # )
        # self.room_group_name = f'chat_{self.room_name}'

        # await self.channel_layer.group_add(
        #     self.room_group_name, self.channel_name
        # )
        await self.accept()

    async def disconnect(self, code):
        if self.chats:
            for chat in self.chats:
                await self.channel_layer.group_discard(
                    chat, self.channel_name
                )
        await delete_spot_record(self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if 'travel' in message:
            for chat in self.chats:
                await self.channel_layer.group_discard(
                    chat, self.channel_name
                )
            self.chats = []
            y, x = message["travel"]["y"], message["travel"]["x"]
            # self.room_name = f'{message["travel"]["y"]}_{message["travel"]["x"]}'
            self.room_name = f'{y}_{x}'
            self.room_group_name = f'chat_{self.room_name}'

            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            self.chats.append(self.room_group_name)
            await create_spot_record(x, y, self.channel_name)
            return

        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat_message', 'message': message}
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
