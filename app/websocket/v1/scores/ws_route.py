# import asyncio
# from app.redis.channels import SCORES_CHANNEL
# from app.websocket.v1.scores.utils import publish


# import asyncio
from fastapi import APIRouter, Depends, WebSocket
import redis.asyncio as AsyncRedis

# from app.core.auth.schema import UserRead
# from app.core.auth.websocket import validate_ws_jwt
from app.redis.client import get_redis_client

import logging

from app.redis.pubsub import RedisPubsub, get_pubsub
from app.websocket.v1.scores.service import ScoreService, get_score_service

logger = logging.getLogger("uvicorn")

router = APIRouter()


@router.websocket("/")
async def ws_welcome(
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


@router.websocket("/add-score")
async def ws_submit_score(
    websocket: WebSocket, redis: AsyncRedis.Redis = Depends(get_redis_client)
):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()

        await redis.publish("score_submission", message=data)

        await websocket.send_text("done")


@router.websocket("/scores")
async def ws_get_scores(
    websocket: WebSocket,
    score_service: ScoreService = Depends(get_score_service),
    # user_data: UserRead | None = Depends(validate_ws_jwt),
    pubsub: RedisPubsub = Depends(get_pubsub),
):
    await websocket.accept()
    # if not user_data:
    # gracefylly exit endpoint
    # return

    await pubsub.subscribe("score_submission")

    async def score_submission_listener(data):
        print(f"got the passed score by user: {data}")
        result = await score_service.get_leaderboard_data("all")
        print(f"got result: {result}")
        await websocket.send_json({"result": result})

    try:
        pubsub.listen(score_submission_listener)

        while True:
            payload: dict = await websocket.receive_json()
            print(f"payload for filtering: {payload.get('game')}")
            result = await score_service.get_leaderboard_data(payload.get("game"))
            # print(f"got result: {result}")
            await websocket.send_json({"result": result})

    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
        logger.info("Websocket connection closed.")
