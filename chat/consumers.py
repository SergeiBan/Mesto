import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis


r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)


async def flush_redis():
    await r.flushall(asynchronous=True)

JUST_STARTED = True
RADIUS = 1000
UNITS = 'km'


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        self.y = None
        self.x = None
        self.nearby = None
        self.prev_nearby = None
        self.nearby_names = None
        super().__init__()

    async def connect(self):
        global JUST_STARTED
        if JUST_STARTED:
            await flush_redis()
            JUST_STARTED = False
        await self.accept()

    async def disconnect(self, code):
        await r.zrem('World', self.channel_name)
        if self.prev_nearby:
            await self.deliver_message(
                self.prev_nearby,
                {'gone': self.channel_name}
            )
        await r.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if 'travel' in message:
            self.y, self.x = message["travel"]["y"], message["travel"]["x"]
            await r.geoadd('World', (self.y, self.x, self.channel_name))

            nearby_coords = await self.get_nearby_people()
            self.nearby_names = set([el[0] for el in nearby_coords])

            if self.prev_nearby:
                await self.deliver_message(
                    self.prev_nearby.difference(self.nearby_names),
                    {'gone': self.channel_name}
                )
            self.prev_nearby = self.nearby_names.copy()

            await self.deliver_message(
                self.nearby_names,
                {'around_me': nearby_coords}
            )

            return

        nearby_coords = await self.get_nearby_people()
        self.nearby_names = set([el[0] for el in nearby_coords])

        await self.deliver_message(self.nearby_names, {'new_message': message})

    async def get_nearby_people(self):
        return await r.geosearch(
            name='World', longitude=self.y, latitude=self.x, unit=UNITS,
            radius=RADIUS, withcoord=True
        )

    async def deliver_message(self, nearby, message):
        for person in nearby:
            await self.channel_layer.send(
                person,
                {'type': 'chat_message', 'message': message}
            )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
