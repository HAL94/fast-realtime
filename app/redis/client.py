import redis.asyncio as redis


redis_client: redis.Redis | None = None


def get_redis_client():
    global redis_client
    if not redis_client:
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
    return redis_client