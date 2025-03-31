from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.common.app_response import AppResponse
from app.core.config import AppSettings
from app.core.setup import create_application
from app.api import router as api_router
from app.websocket import router as ws_router
from app.utils.leaderboard import generate_leaderboard_data


app = create_application(
    api_router=api_router, ws_router=ws_router, settings=AppSettings()
)


leaderboard = []
@app.post("/")
async def generate_leaderboard():
    global leaderboard
    leaderboard = generate_leaderboard_data()
    return {"success": True}

@app.exception_handler(Exception)
async def generic_exception_logger(request: Request, exc: Exception):
    """Logs all unhandled exceptions and returns a proper response."""
    error_msg = exc.__str__()
    # logger.exception(f"An unhandled exception occurred: {error_msg}")
    app_response = AppResponse(success=False, status_code=500, message=(
                f"Failed method {request.method} at URL {request.url}."
                f" Exception message is: {error_msg}."
            ))
    return JSONResponse(content=app_response.__dict__)
