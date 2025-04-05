# import asyncio
# from app.redis.channels import SCORES_CHANNEL
# from app.websocket.v1.scores.utils import publish

from fastapi import APIRouter, Depends, WebSocket
import redis.asyncio as AsyncRedis

from app.core.auth.schema import UserRead
from app.core.auth.websocket import validate_ws_jwt
from app.redis.client import get_redis_client

import logging

from app.websocket.v1.scores.service import ScoreService, get_score_service

logger = logging.getLogger("uvicorn")

router = APIRouter()


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


@router.websocket("/scores")
async def websocket_user1_score(
    websocket: WebSocket,
    score_service: ScoreService = Depends(get_score_service),
    user_data: UserRead | None = Depends(validate_ws_jwt),
):
    if not user_data:
        # gracefylly exit endpoint
        return

    try:
        while True:            
            payload: dict = await websocket.receive_json()
            print(f"payload for filtering: {payload.get('game')}")
            result = await score_service.get_leaderboard_data(payload.get('game'))
            print(f"got result: {result}")
            await websocket.send_json({"result": result})
    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
        logger.info("Websocket connection closed.")
