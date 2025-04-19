import asyncio
from fastapi import Depends
import redis.asyncio as AsyncRedis

from app.redis.client import get_redis_client


def get_pubsub(client: AsyncRedis.Redis = Depends(get_redis_client)):
    return RedisPubsub(client=client)


class RedisPubsub:
    def __init__(self, client: AsyncRedis.Redis):
        self.pubsub = client.pubsub()

    async def subscribe(self, channel: str, *args, **kwargs):
        await self.pubsub.subscribe(channel, args=args, kwargs=kwargs)

    def listen(self, listener_func, *args, **kwargs):
        async def run_task():
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = message["data"].decode("utf-8")
                    await listener_func(data, *args, **kwargs)

        listener_task = asyncio.create_task(run_task())

        return listener_task

    async def unsubscribe(self, channel: str):
        await self.pubsub.unsubscribe(channel)

    async def close(
        self,
    ):
        await self.pubsub.close()
