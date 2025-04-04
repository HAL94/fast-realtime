from typing import ClassVar, Generic, TypeVar
from pydantic import BaseModel
import redis.asyncio as redis

from app.redis.schema import ZRangeItem, ZRangeItemList


redis_client: redis.Redis | None = None


def get_redis_client():
    global redis_client
    if not redis_client:
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
    return redis_client


PydanticModel = TypeVar("P", bound=BaseModel)


class BaseRedis(Generic[PydanticModel]):
    __model__: ClassVar[PydanticModel]

    def __init__(self, client: redis.Redis):
        self.client = client

    @property
    def _model(self) -> PydanticModel:
        return self.__model__

    async def zrange(
        self, *, key: str, start: int = 0, end: int = -1, withscores: bool = True
    ) -> ZRangeItemList:
        try:
            data = await self.client.zrange(
                key, start=start, end=end, withscores=withscores
            )

            result = []
            for item in data:
                key, score = item
                item_ = ZRangeItem(key=key.decode(), score=score)
                result.append(item_)

            return ZRangeItemList(result=result)

        except Exception as e:
            print(f"error occured at func: ZRANGE: {e}")

    async def zrevrange(
        self, *, key: str, start: int = 0, end: int = -1, withscores: bool = True
    ):
        try:
            data = await self.client.zrevrange(
                key, start=start, end=end, withscores=withscores
            )

            result = []
            for item in data:
                key, score = item
                item_ = ZRangeItem(key=key, score=score)
                result.append(item_)

            return ZRangeItemList(result=result)

        except Exception as e:
            print(f"error occured at func: ZERVRANGE: {e}")

    async def hgetall(self, *, name: str) -> PydanticModel | None:
        try:
            item_dict = await self.client.hgetall(name=name)

            if not item_dict or len(item_dict) == 0:
                return None
            
            item_dict = {k.decode(): v.decode() for k, v in item_dict.items()}

            return self._model(**item_dict)
        
        except Exception as e:
            print(f"error occured at func: HGETALL: {e}")
