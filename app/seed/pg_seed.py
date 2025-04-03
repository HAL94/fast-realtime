from sqlalchemy import insert
from sqlalchemy.orm import Session

from passlib.context import CryptContext

from app.core.auth.schema import UserSignupRequest
from app.seed.base import SeederBase
from app.seed.utils import create_session_local, get_db
from ..core.db.models import User

class UserSeeder(SeederBase):
    name = "User Seeder"

    def __init__(self):
        super().__init__()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _create_hashed_pw(self, password: str):
        return self.pwd_context.hash(password)

    def transform(self, _data):
        pass

    def seed(self, num_entries, db: Session):
        fake = self.fake

        data = [
            UserSignupRequest(
                **User(
                    name=fake.name(),
                    email=fake.email(),
                    password=self._create_hashed_pw("123456"),
                ).__dict__
            ).model_dump()
            for _ in range(num_entries)
        ]

        created_data = db.scalars(insert(User).values(data).returning(User)).all()

        db.commit()

        return created_data


def seed_database():
    """Seeds the user database with initial data."""
    SessionLocal = create_session_local()
    db = next(get_db(SessionLocal=SessionLocal))
    seeders = [UserSeeder()]
    try:
        for seeder in seeders:
            data = seeder.seed(num_entries=10, db=db)
            print(f"created data: {data}")
            print(f"Seeder: {seeder.name} is finished successfully")
    except Exception as e:
        print(f"Error seeding database for {seeder.name}: {e}")


if __name__ == "__main__":
    seed_database()
