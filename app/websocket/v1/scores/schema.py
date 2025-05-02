from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.core.common.app_response import AppBaseModel


class PlayerRank(AppBaseModel):
    rank: Optional[int] = -1
    user_id: int
    player: str
    game: str
    score: int
    date: Optional[str | datetime] = None


class PlayerRankAdd(BaseModel):
    user_id: int
    player: str
    game: str
    score: int
    date: str | datetime


class SubmitScore(AppBaseModel):
    score: int
    game_channel: str

class ReportRequest(AppBaseModel):
    start: datetime
    end: datetime
    limit: Optional[int] = None
    
class ReportResponse(AppBaseModel):
    name: str
    score: int
    games: int