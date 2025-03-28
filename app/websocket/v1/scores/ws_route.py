
# import asyncio
# from app.redis.channels import SCORES_CHANNEL
# from app.websocket.v1.scores.utils import publish
from fastapi import APIRouter, Depends, WebSocket
import redis.asyncio as redis

from app.redis.client import get_redis_client


router = APIRouter()
scores_sorted_set = "scores"


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, redis: redis.Redis = Depends(get_redis_client)):
    await websocket.accept()

    await websocket.send_text("Welcome to your websocket server")
    # await asyncio.sleep(0.2)
    # await redis.publish(SCORES_CHANNEL, "")

    while True:
        data = await websocket.receive_text()
        print(f"received: {data}")
        # await publish(data)
        await websocket.send_text(f"Message text was: {data}")
        

@router.websocket("/u1")
async def websocket_user1_score(websocket: WebSocket, redis: redis.Redis = Depends(get_redis_client)):
    await websocket.accept()
    try:
        data = await redis.zrange(scores_sorted_set, 0, -1, withscores=True)
        await websocket.send_json({"result": [t[1] for t in data]})
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
    except Exception as e:
        print(f"Websocket error: {e}")