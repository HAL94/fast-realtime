from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.core.common.app_response import ModelCamelized


class PlayerRank(BaseModel):
    rank: int
    id: int
    player: str
    game: str
    score: int
    date: Optional[str | datetime] = None


class PlayerRankAdd(BaseModel):
    id: int
    player: str
    game: str
    score: int
    date: str | datetime


class SubmitScore(ModelCamelized):
    score: int
    game_channel: str
