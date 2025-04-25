import json
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
import redis.asyncio as AsyncRedis

from app.core.auth.schema import UserRead
from app.core.auth.websocket import revalidate_token, validate_ws_jwt
from app.core.common.app_response import WsAppResponse
from app.redis.client import get_redis_client

import logging

from app.redis.events import SCORE_SUBMISSION, USER_SCORE
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
    pubsub: RedisPubsub = Depends(get_pubsub),
):
    if not user_data:
        return

    try:

        async def get_updated_user_score(data: Optional[str] = None):
            await revalidate_token(websocket)
            print(f"Got some data: {data}")
            user_score = await scores_service.get_top_user_score(user_data.id)
            result = user_score.model_dump() if user_score else None
            await websocket.send_json({"result": result})

        await get_updated_user_score()

        await pubsub.subscribe(f"{USER_SCORE}{user_data.id}")

        listener_task = pubsub.listen(get_updated_user_score)

        while True:
            # Just calling the receive_taxt to keep alive. Or use any other keep-alive mechanism
            await websocket.receive_text()
            # Optionally revalidate token periodically here if needed
            # await asyncio.sleep(some_interval)

    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"{USER_SCORE}{user_data.id}")
        if listener_task and not listener_task.cancelled():
            listener_task.cancel()


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
            # data = await websocket.receive_json()
            try:
                data = await websocket.receive_json()
                data = SubmitScore.model_validate(data)
            except ValueError as e:
                logger.info(f"Data validation error: {e}")
                ws_error = WsAppResponse(error="Invalid Request")
                await websocket.send_json(ws_error.model_dump())
                continue

            # print(f"received data from client: {data}")

            await scores_service.add_user_score(data=data, user_data=user_data)
            await redis.publish(SCORE_SUBMISSION, message=json.dumps(data.model_dump()))
            await redis.publish(
                f"{USER_SCORE}{user_data.id}", message="UPDATE_SCORE_FETCH_FLAG"
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

    await pubsub.subscribe(SCORE_SUBMISSION)

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
            game_channel = payload.get("game")
            # print(f"payload for filtering: {game_channel}")
            print(f"pagination params: {payload.get('start')} - {payload.get('end')}")
            result = await score_service.get_leaderboard_data(
                game_channel, start=payload.get("start"), end=payload.get("end")
            )
            total_count = await score_service.get_leaderboard_count(
                game_channel=game_channel
            )
            await websocket.send_json({"result": result, "totalCount": total_count})

    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except WebSocketDisconnect:
        logger.info("Websocket Disconnected (/scores)")
        await pubsub.unsubscribe(SCORE_SUBMISSION)
        listener_task.cancel()
