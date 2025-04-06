

from pydantic import BaseModel


class GameChannel(BaseModel):
    label: str
    value: str
    

    