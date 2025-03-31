import jwt
from app.core.auth.exceptions import InvalidTokenError
from app.core.auth.repository import UserRepository
from app.core.auth.schema import UserRead
from app.core.config import AppSettings
from app.core.logger import logger

from jwt.exceptions import ExpiredSignatureError
from app.core.exceptions import UnauthorizedException


class BaseJwtAuth:
    def __init__(self, user_repo: UserRepository, settings: AppSettings):
        self.user_repo = user_repo
        self.settings = settings

    async def _validate_token(self, token: str) -> UserRead:
        """Validate JWT token and return user with decoded payload"""
        try:
            if not token:
                raise UnauthorizedException("Missing authentication token")

            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )

            user_id = payload.get("id")
            if not user_id:
                raise UnauthorizedException("Token payload missing user ID")

            user_found = await self.user_repo.get_one(val=user_id, field="id")
            if not user_found:
                raise UnauthorizedException

            # Optional: Check if user is active/enabled

            return user_found

        except ExpiredSignatureError:
            logger.info("Token has expired")
            raise UnauthorizedException
        except InvalidTokenError:
            logger.info("Token is invalid")
            raise UnauthorizedException
