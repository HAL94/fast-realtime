import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
import redis.asyncio as AsyncRedis

from app.core.auth.schema import UserRead
from app.core.auth.websocket import revalidate_token, validate_ws_jwt
from app.redis.client import get_redis_client

import logging

from app.redis.pubsub import RedisPubsub, get_pubsub
from app.websocket.v1.scores.schema import SubmitScore
from app.websocket.v1.scores.service import ScoreService, get_score_service

logger = logging.getLogger("uvicorn")

router = APIRouter()


@router.websocket("/")
async def ws_welcome(
    websocket: WebSocket,
):
    await websocket.accept()

    await websocket.send_text("Welcome to your websocket server")

    while True:
        data = await websocket.receive_text()
        print(f"received: {data}")
        # await publish(data)
        await websocket.send_text(f"Message text was: {data}")


@router.websocket("/my-score")
async def ws_user_score(
    websocket: WebSocket,
    scores_service: ScoreService = Depends(get_score_service),
    user_data: UserRead = Depends(validate_ws_jwt),
):
    if not user_data:
        return

    try:
        user_score = await scores_service.get_top_user_score(user_data.id)
        # print(f"got user data: {user_score}")
        result = user_score.model_dump() if user_score else None
        await websocket.send_json({"result": result})
    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
        logger.info("Websocket connection closed.")


@router.websocket("/add-score")
async def ws_submit_score(
    websocket: WebSocket,
    redis: AsyncRedis.Redis = Depends(get_redis_client),
    user_data: UserRead | None = Depends(validate_ws_jwt),
    scores_service: ScoreService = Depends(get_score_service),
):
    if not user_data:
        return
    try:
        while True:
            await revalidate_token(websocket)
            data = await websocket.receive_json()
            data = SubmitScore.model_validate(data)
            # print(f"received data from client: {data}")

            await scores_service.add_user_score(data=data, user_data=user_data)
            await redis.publish(
                "score_submission", message=json.dumps(data.model_dump())
            )
    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        await redis.close()
    except WebSocketDisconnect:
        await redis.close()
        logger.info("Websocket connection closed (/add-score).")


@router.websocket("/scores")
async def ws_get_scores(
    websocket: WebSocket,
    score_service: ScoreService = Depends(get_score_service),
    user_data: UserRead | None = Depends(validate_ws_jwt),
    pubsub: RedisPubsub = Depends(get_pubsub),
):
    if not user_data:
        # gracefylly exit endpoint
        return

    await pubsub.subscribe("score_submission")

    try:

        async def score_submission_listener(data):
            data = json.loads(data)
            # print(f"got the passed score by user: {data}")
            result = await score_service.get_leaderboard_data("all")
            await websocket.send_json({"result": result})

        listener_task = pubsub.listen(score_submission_listener)

        while True:
            await revalidate_token(websocket)
            payload: dict = await websocket.receive_json()
            print(f"payload for filtering: {payload.get('game')}")
            result = await score_service.get_leaderboard_data(payload.get("game"))
            await websocket.send_json({"result": result})

    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except WebSocketDisconnect:
        logger.info("Websocket Disconnected (/scores)")
        await pubsub.unsubscribe("score_submission")
        listener_task.cancel()
