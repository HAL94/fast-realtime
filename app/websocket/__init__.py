from fastapi import APIRouter
from app.websocket.v1 import router as ws_router

router = APIRouter(prefix="/ws")

router.include_router(ws_router)