from typing import Optional
from pydantic import BaseModel

from app.core.common.app_response import AppBaseModel


class GameChannel(BaseModel):
    label: str
    value: str


class AllGameChannelsQuery(AppBaseModel):
    exclude_channel: Optional[str] = None
