

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PlayerRank(BaseModel):
    rank: int
    id: int
    player: str
    game: str
    score: int
    date: Optional[str | datetime] = None

