

from typing import Any
from pydantic import BaseModel


class ZRangeItem(BaseModel):
    key: str
    score: Any
    
class ZRangeItemList(BaseModel):
    result: list[ZRangeItem]