

from typing import Optional
from pydantic import BaseModel


class UserRead(BaseModel):
    id: str | int
    name: Optional[str] = None
    email: str
    
class UserData(BaseModel):
    user: UserRead
    token: str
    
