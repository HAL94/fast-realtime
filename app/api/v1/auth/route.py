from fastapi import APIRouter, Depends, Response

from app.core.auth.schema import (
    UserRead,
    UserSigninRequest,
    UserSignupRequest,
    UserSignupResponse,
)
from app.core.auth.http import validate_http_jwt
from app.api.v1.auth.service import AuthService, get_auth_service
from app.core.common.app_response import AppResponse
from app.core.exceptions import AlreadyExistsException, UnauthorizedException

from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login(
    payload: UserSigninRequest, response: Response, auth_service: AuthService = Depends(get_auth_service),
):
    data = await auth_service.login_user(payload)
    response.set_cookie('ath', data.token, httponly=True, samesite='lax', max_age=60000)
    return AppResponse(data=data)


@router.get("/me", response_model=AppResponse[UserRead])
async def get_user(user_data: UserRead = Depends(validate_http_jwt)):
    try:
        return AppResponse(
            data=user_data
        )
    except InvalidTokenError as e:
        raise UnauthorizedException("Unauthorized") from e
    except ExpiredSignatureError as e:
        raise UnauthorizedException(detail="Your session has expired") from e
    except UnauthorizedException as e:
        raise e

@router.post("/signout")
async def signout_user(response: Response):
    response.delete_cookie('ath')
    
    return AppResponse(data=None, message="You logged out successfully")
    

@router.post("/signup", response_model=AppResponse[UserSignupResponse])
async def signup_user(
    payload: UserSignupRequest, auth_service: AuthService = Depends(get_auth_service)
):
    try:
        data = await auth_service.sign_up_user(payload=payload)
        return AppResponse(data=data, status_code=201)
    except AlreadyExistsException as e:
        raise e
