from fastapi import APIRouter, Depends

from app.core.auth.schema import UserData, UserSigninRequest, UserSignupRequest, UserSignupResponse
from app.core.auth.http import validate_http_jwt
from app.api.v1.auth.service import AuthService, get_auth_service
from app.core.common.app_response import AppResponse
from app.core.exceptions import AlreadyExistsException, UnauthorizedException

from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AppResponse[UserData])
async def login(payload: UserSigninRequest, auth_service: AuthService = Depends(get_auth_service)):
    data = await auth_service.login_user(payload)    
    return AppResponse(data=data)

@router.get("/me", response_model=AppResponse[UserData])
async def get_user(user_data: UserData = Depends(validate_http_jwt)):
    try:
        return AppResponse(data=user_data)
    except InvalidTokenError as e:
        raise UnauthorizedException from e
    except ExpiredSignatureError as e:
        raise UnauthorizedException(detail="Your session has expired") from e
    except UnauthorizedException as e:
        raise e

@router.post("/signup", response_model=AppResponse[UserSignupResponse])
async def signup_user(payload: UserSignupRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        data = await auth_service.sign_up_user(payload=payload)
        return AppResponse(data=data, status_code=201)
    except AlreadyExistsException as e:
        raise e