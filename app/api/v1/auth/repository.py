from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.v1.auth.schema import UserRead
from app.core.db.base_repo import BaseRepo
from app.core.db.database import get_async_session
from app.core.db.models import User

def get_user_repo(db: AsyncSession = Depends(get_async_session)):
    return UserRepository(session=db)

class UserRepository(BaseRepo[User, UserRead]):
    __dbmodel__ = User
    __model__ = UserRead
    