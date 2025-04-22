from fastapi import APIRouter, Depends, Query
from app.api.v1.games.schema import AllGameChannelsQuery, GameChannel
from app.api.v1.games.utils import get_game_channels
from app.core.auth.http import validate_http_jwt
from app.core.common.app_response import AppResponse

router = APIRouter(prefix="/games", tags=["Games"])


@router.get(
    "/",
    response_model=AppResponse[list[GameChannel]],
    dependencies=[Depends(validate_http_jwt)],
)
async def get_all_games(exclude: AllGameChannelsQuery = Query(...)):    
    data = get_game_channels(exclude=exclude.exclude_channel)
    return AppResponse(data=data)
