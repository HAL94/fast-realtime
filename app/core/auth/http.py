from fastapi import Depends

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.auth.base import BaseJwtAuth
from app.core.auth.repository import UserRepository, get_user_repo
from app.core.auth.schema import AccessToken
from app.core.config import AppSettings, get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException

security = HTTPBearer()


async def validate_http_jwt(
    user_repo: UserRepository = Depends(get_user_repo),
    settings: AppSettings = Depends(get_settings),
    credentials: HTTPAuthorizationCredentials = Depends(security),
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
        credentials: HTTPAuthorizationCredentials,
    ):
        super().__init__(user_repo=user_repo, settings=settings)
        self.credentials = credentials

    async def validate_http_token(self):
        if not self.credentials:
            raise ForbiddenException("Could not find authorization header")

        if self.credentials.scheme != "Bearer":
            raise ForbiddenException("Invalid authorization scheme")

        token: AccessToken = self.credentials.credentials

        user_info = await self._validate_token(token)

        if not user_info:
            raise UnauthorizedException

        return user_info
