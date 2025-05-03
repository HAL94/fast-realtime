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
from app.websocket.v1.scores.schema import (
    GetLeaderboardRequest,
    GetLeaderboardResponse,
    ReportRequest,
    SubmitScore,
)
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
        payload_cache: GetLeaderboardRequest | None = None

        async def score_submission_listener(data):
            data = json.loads(data)
            # print(f"got the passed score by user: {data}")
            if not payload_cache:
                channel = "all"
                start = 0
                end = -1

            if isinstance(payload_cache, GetLeaderboardRequest):
                channel = payload_cache.game or "all"
                start = payload_cache.start or 0
                end = payload_cache.end or -1

            result, total_count = await score_service.get_leaderboard_data(
                channel, start=start, end=end
            )

            result = GetLeaderboardResponse(result=result, total_count=total_count)
            await websocket.send_json(result.model_dump())

        listener_task = pubsub.listen(score_submission_listener)

        while True:
            await revalidate_token(websocket)
            try:
                payload = await websocket.receive_json()
                payload = GetLeaderboardRequest.model_validate(payload)
            except ValueError:
                error = WsAppResponse(error="Invalid request for leaderboard")
                await websocket.send_json(error.model_dump())

            payload_cache = payload
            game_channel = payload.game
            result, total_count = await score_service.get_leaderboard_data(
                game_channel, start=payload.start, end=payload.end
            )

            result = GetLeaderboardResponse(result=result, total_count=total_count)
            await websocket.send_json(result.model_dump())

    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except WebSocketDisconnect:
        logger.info("Websocket Disconnected (/scores)")
        await pubsub.unsubscribe(SCORE_SUBMISSION)
        listener_task.cancel()


@router.websocket("/reports")
async def ws_get_report(
    websocket: WebSocket,
    score_service: ScoreService = Depends(get_score_service),
    user_data: UserRead | None = Depends(validate_ws_jwt),
):
    if not user_data:
        return
    
    print(f"user_id: {user_data.id}")

    try:
        while True:
            await revalidate_token(websocket)
            try:
                payload = await websocket.receive_json()
                payload = ReportRequest.model_validate(payload)
            except ValueError:
                error = WsAppResponse(error="Invalid Request")
                await websocket.send_json(error.model_dump())
                continue

            result = await score_service.get_reports(payload)
            await websocket.send_json({"result": result})

    except WebSocketDisconnect:
        logger.info("Websocket Disconnected (/reports)")
    except AsyncRedis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
