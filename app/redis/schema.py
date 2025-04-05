

from typing import Optional
from pydantic import BaseModel


class ZRangeItem(BaseModel):
    key: str
    score: Optional[float] = None
    
class ZRangeItemList(BaseModel):
    result: list[ZRangeItem]