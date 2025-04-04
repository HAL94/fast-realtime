from http.cookies import SimpleCookie
from fastapi import Depends, WebSocket
from app.core.auth.base import BaseJwtAuth
from app.core.auth.repository import UserRepository, get_user_repo
from app.core.auth.schema import AccessToken
from app.core.auth.utils import close_unauthorized_ws
from app.core.config import AppSettings, get_settings
from app.core.exceptions import UnauthorizedException


def get_ws_token(websocket: WebSocket):
    cookie = SimpleCookie()
    cookie.load(websocket.headers.get("cookie"))
    cookies = {key: value.value or None for key, value in cookie.items()}

    token: AccessToken = cookies.get("ath")
    return token or None


async def validate_ws_jwt(
    websocket: WebSocket,
    token: str = Depends(get_ws_token),
    user_repo: UserRepository = Depends(get_user_repo),
    settings: AppSettings = Depends(get_settings),
):
    jwt_auth = WsJwtAuth(user_repo=user_repo, settings=settings)    
    return await jwt_auth.validate_ws_token(websocket=websocket, token=token)


class WsJwtAuth(BaseJwtAuth):
    def __init__(self, user_repo: UserRepository, settings: AppSettings):
        super().__init__(user_repo=user_repo, settings=settings)

    async def validate_ws_token(self, websocket: WebSocket, token: str | None):
        await websocket.accept()
        try:
            return await self._validate_token(token)
        except UnauthorizedException:
            await close_unauthorized_ws(websocket=websocket)
            pass
