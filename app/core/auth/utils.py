from fastapi import WebSocket, status
from app.core.logger import logger


async def close_unauthorized_ws(websocket: WebSocket, reason="Unauthorized"):
    try:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=reason)
        logger.info(
            {
                "path": str(websocket.url.path),
                "message": "Unauthorized WebSocket connection (401)",
            }
        )
    except Exception:
        pass
