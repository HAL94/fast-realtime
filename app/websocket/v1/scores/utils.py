
import redis.asyncio as redis

async def publish(channel: str, score: int | str, redis: redis.Redis):
    global user_id
    user_id += 1
    id = f"u{user_id}"
    await redis.zadd(channel, {id: score})
    await redis.publish(channel, "")