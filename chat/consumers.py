import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis


r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)


async def flush_redis():
    await r.flushall(asynchronous=True)

JUST_STARTED = True


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        self.y = None
        self.x = None
        self.nearby = None
        super().__init__()

    async def connect(self):
        global JUST_STARTED
        if JUST_STARTED:
            await flush_redis()
            JUST_STARTED = False
        await self.accept()

    async def disconnect(self, code):
        await r.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if 'travel' in message:

            self.y, self.x = message["travel"]["y"], message["travel"]["x"]

            self.nearby = await get_nearby_people(self.y, self.x, r)
            if self.nearby == 0:
                return

            for person in self.nearby:
                await self.channel_layer.send(
                    person,
                    {'type': 'chat_message', 'message': f'y {self.y} x {self.x}'}
                )
            await deliver_message(self, self.nearby, f'y {self.y} x {self.x}')
            await r.geoadd('World', (self.y, self.x, self.channel_name))
            return

        self.nearby = await get_nearby_people(self.y, self.x, r)       
        await deliver_message(self, self.nearby, message)
        print(self.nearby, message)

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))


async def get_nearby_people(y, x, r):
    return await r.geosearch(
        name='World', longitude=y, latitude=x, unit='km', radius=1000)


async def deliver_message(consumer, nearby, message):
    for person in nearby:
        await consumer.channel_layer.send(
            person,
            {'type': 'chat_message', 'message': message}
        )
