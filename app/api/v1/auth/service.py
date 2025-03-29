from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.exceptions import InvalidTokenError

from app.api.v1.auth.repository import UserRepository, get_user_repo
from app.api.v1.auth.schema import UserData, UserRead
from app.core.config import AppSettings, get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException

security = HTTPBearer()
class JwtBearer:
    async def __call__(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        user_repo: UserRepository = Depends(get_user_repo),
        settings: AppSettings = Depends(get_settings),
    ):
        if not credentials:
            raise ForbiddenException("Could not find authorization header")

        if credentials.scheme != "Bearer":
            raise ForbiddenException("Invalid authorization scheme")

        token = credentials.credentials

        self.user_repo = user_repo
        self.settings = settings

        user_info = await self.get_current_user(token)

        return UserData(token=token, user=user_info)

    async def get_current_user(self, token: str) -> UserRead:
        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            if not user_id:
                raise UnauthorizedException

            return await self.user_repo.get_one(val=user_id, field="id")
        except InvalidTokenError as e:
            raise UnauthorizedException from e
        except Exception:
            raise UnauthorizedException

