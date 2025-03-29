from fastapi import APIRouter, Depends

from app.api.v1.auth.schema import UserData
from app.api.v1.auth.service import JwtBearer
from app.core.common.app_response import AppResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login():
    return {"todo": "not yet implemented"}

@router.get("/me", response_model=AppResponse[UserData])
async def get_user(user_data: UserData = Depends(JwtBearer())):
    return AppResponse(data=user_data)