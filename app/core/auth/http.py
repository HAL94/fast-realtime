from fastapi import Depends, Request

from fastapi.security import APIKeyCookie, HTTPBearer
from app.core.auth.base import BaseJwtAuth
from app.core.auth.repository import UserRepository, get_user_repo
from app.core.auth.schema import AccessToken
from app.core.config import AppSettings, get_settings
from app.core.exceptions import UnauthorizedException
from app.core.logger import logger

security = HTTPBearer()
cookie = APIKeyCookie(name='ath')

async def get_token_cookie(request: Request) -> AccessToken:
    try:
        return await cookie(request)
    except Exception as e:
        raise UnauthorizedException from e


async def validate_http_jwt(
    user_repo: UserRepository = Depends(get_user_repo),
    settings: AppSettings = Depends(get_settings),
    credentials: str = Depends(get_token_cookie),
):
    jwt_auth = HttpJwtAuth(
        user_repo=user_repo, settings=settings, credentials=credentials
    )
    return await jwt_auth.validate_http_token()


class HttpJwtAuth(BaseJwtAuth):
    def __init__(
        self,
        user_repo: UserRepository,
        settings: AppSettings,
        credentials: str,
    ):
        super().__init__(user_repo=user_repo, settings=settings)
        self.credentials = credentials

    async def validate_http_token(self):
        if not self.credentials:
            logger.info("no creds")
            raise UnauthorizedException("Could not find authorization header")

        token: AccessToken = self.credentials

        user_info = await self._validate_token(token)

        if not user_info:
            raise UnauthorizedException

        return user_info
