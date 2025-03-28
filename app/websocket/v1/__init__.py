from fastapi import APIRouter
from app.websocket.v1.scores.ws_route import router as scores_ws_route

router = APIRouter(prefix="/v1")

router.include_router(scores_ws_route)