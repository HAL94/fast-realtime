# import asyncio
# from app.redis.channels import SCORES_CHANNEL
# from app.websocket.v1.scores.utils import publish

from fastapi import APIRouter, Depends, WebSocket
import redis.asyncio as AsyncRedis

from app.core.auth.schema import UserRead
from app.core.auth.websocket import validate_ws_jwt
from app.redis.client import get_redis_client

import logging

logger = logging.getLogger("uvicorn")

router = APIRouter()
scores_sorted_set = "scores"


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket, redis: AsyncRedis.Redis = Depends(get_redis_client)
):
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
async def websocket_user1_score(
    websocket: WebSocket,
    redis: AsyncRedis.Redis = Depends(get_redis_client),
    user_data: UserRead | None = Depends(validate_ws_jwt),
):    
    if not user_data:
        # gracefylly exit endpoint
        return
    
    print(f"token is: {user_data.token}")

    try:
        data = await redis.zrange(scores_sorted_set, 0, -1, withscores=True)
        await websocket.send_json({"result": [t[1] for t in data]})
    except AsyncRedis.ConnectionError as e:
        print(f"Redis connection error: {e}")
        
   
