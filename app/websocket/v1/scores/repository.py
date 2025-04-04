from fastapi import Depends
import redis.asyncio as redis
from app.redis.client import BaseRedis, get_redis_client
from app.websocket.v1.scores.schema import PlayerRank


async def get_scores_repo(redis_client: redis.Redis = Depends(get_redis_client)):
    return ScoresRepository(client=redis_client)


class ScoresRepository(BaseRedis[PlayerRank]):
    __model__ = PlayerRank
