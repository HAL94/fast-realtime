from typing import Optional
from pydantic import BaseModel

type AccessToken = str


class UserRead(BaseModel):
    id: str | int
    name: Optional[str] = None
    email: str


class UserReadWithPw(BaseModel):
    id: str | int
    name: Optional[str] = None
    email: str
    password: str


class UserData(BaseModel):
    user: UserRead
    token: AccessToken


class UserSignupRequest(BaseModel):
    email: str
    name: Optional[str] = None
    password: str


class UserSignupResponse(UserRead):
    pass


class UserSigninRequest(BaseModel):
    email: str
    password: str


class UserSigninResponse(UserData):
    pass
    
