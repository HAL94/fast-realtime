from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.common.app_response import AppResponse
from app.core.config import AppSettings
from app.core.logger import logger
from app.core.setup import create_application
from app.api import router as api_router
from app.websocket import router as ws_router

app = create_application(
    api_router=api_router, ws_router=ws_router, settings=AppSettings()
)


@app.get("/welcome")
async def welcome():
    return {"success": True}


@app.exception_handler(Exception)
async def generic_exception_logger(request: Request, exc: Exception):
    """Logs all unhandled exceptions and returns a proper response."""
    error_msg = exc.__str__()
    # logger.exception(f"An unhandled exception occurred: {error_msg}")
    app_response = AppResponse(
        success=False,
        status_code=500,
        message=(
            f"Failed method {request.method} at URL {request.url}."
            f" Exception message is: {error_msg}."
        ),
    )
    return JSONResponse(content=app_response.model_dump(by_alias=True))


@app.exception_handler(HTTPException)
async def unauth_handler(request: Request, exc: HTTPException):
    logger.info(
        f"Request Failed: URL: {request.url}. Method: {request.method} Status code is: {exc.status_code}"
    )
    default_response = AppResponse(
        success=False,
        status_code=exc.status_code,
        message="Internal Server Error",
        data=None,
    )
    response_info = (
        AppResponse(**exc.detail) if isinstance(exc.detail, dict) else default_response
    )
    return JSONResponse(
        content=response_info.model_dump(by_alias=True), status_code=exc.status_code
    )
