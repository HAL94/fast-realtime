from fastapi import APIRouter, Depends
from app.api.v1.games.schema import GameChannel
from app.core.auth.http import validate_http_jwt
from app.core.common.app_response import AppResponse
from app.redis.channels import channels_dict

router = APIRouter(
    prefix="/games", tags=["Games"]
)


@router.get("/", response_model=AppResponse[list[GameChannel]], dependencies=[Depends(validate_http_jwt)])
async def get_all_games():
    data = [GameChannel(label=v, value=k) for k, v in channels_dict.items()]
    return AppResponse(data=data)
