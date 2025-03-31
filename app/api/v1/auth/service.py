from datetime import datetime, timedelta, timezone
from fastapi import Depends
import jwt

from app.core.auth.repository import UserRepository, get_user_repo
from app.core.auth.schema import (
    AccessToken,
    JwtData,
    UserRead,
    UserReadWithPw,
    UserSigninRequest,
    UserSigninResponse,
    UserSignupRequest,
    UserSignupResponse,
)
from app.core.config import AppSettings, get_settings
from app.core.exceptions import (
    AlreadyExistsException,
    UnauthorizedException,
)

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    settings: AppSettings = Depends(get_settings),
):
    return AuthService(user_repo=user_repo, settings=settings)

class AuthService:
    def __init__(self, user_repo: UserRepository, settings: AppSettings):
        self.user_repo = user_repo
        self.settings = settings

    def _create_password_hash(self, password: str):
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    def _create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )
        return encoded_jwt

    async def sign_up_user(self, payload: UserSignupRequest):
        user_data: UserRead = await self.user_repo.get_one(
            val=payload.email, field="email"
        )

        if user_data:
            raise AlreadyExistsException

        encrypted_pw = self._create_password_hash(payload.password)

        signup_data = UserSignupRequest(
            email=payload.email, name=payload.name, password=encrypted_pw
        )

        created_user: UserSignupResponse = await self.user_repo.create(data=signup_data)

        return created_user

    async def login_user(self, payload: UserSigninRequest):
        user_data: UserReadWithPw = await self.user_repo.get_one(
            val=payload.email, field="email", return_model=UserReadWithPw
        )

        if not user_data:
            raise UnauthorizedException(detail="Invalid credentials")

        password_match = self._verify_password(
            plain_password=payload.password, hashed_password=user_data.password
        )

        if not password_match:
            raise UnauthorizedException(detail="Invalid credentials")

        jwt_data = JwtData(
            id=user_data.id, name=user_data.name, email=user_data.email
        ).model_dump()

        token: AccessToken = self._create_access_token(data=jwt_data)

        login_data = UserSigninResponse(
            token=token,
            user=UserRead(id=user_data.id, name=user_data.name, email=user_data.email),
        )

        return login_data
