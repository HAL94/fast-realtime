

from sqlalchemy import String
from app.core.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = 'users'
    
    name: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str] = mapped_column(String(16))