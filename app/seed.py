from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from passlib.context import CryptContext
from faker import Faker

from .core.config import AppSettings
from .core.db.database import Base
from .core.db.models import User


class SeederBase(ABC):
    name: str

    def __init__(self):
        settings = AppSettings()
        URL = f"postgresql://{settings.PG_USER}:{settings.PG_PW}@{settings.PG_SERVER}:{
            settings.PG_PORT
        }/{settings.PG_DB}"
        engine = create_engine(url=URL)
        Base.metadata.create_all(bind=engine)  # Create the table if it doesnt exist
        SessionLocal = sessionmaker(bind=engine)

        self.engine = engine
        self.SessionLocal = SessionLocal
        self.settings = settings
        self.fake = Faker()

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            db.rollback()
            print(f"an error occured: {e}")
        finally:
            db.close()

    @abstractmethod
    def seed(self):
        pass


class UserSeeder(SeederBase):
    name = "User Seeder"

    def __init__(self):
        super().__init__()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _create_hashed_pw(self, password: str):
        return self.pwd_context.hash(password)

    def seed(self):
        fake = self.fake
        db = next(self.get_db())

        users_to_seed = [
            User(
                name=fake.name(),
                email=fake.email(),
                password=self._create_hashed_pw("123456"),
            )
            for _ in range(10)
        ]

        db.bulk_save_objects(users_to_seed)
        db.commit()
        print("Database seeded successfully.")


def seed_database():
    """Seeds the user database with initial data."""
    seeders = [UserSeeder()]
    try:
        for seeder in seeders:
            seeder.seed()
            print(f"Seeder: {seeder.name} is finished successfully")
    except Exception as e:
        print(f"Error seeding database for {seeder.name}: {e}")


if __name__ == "__main__":
    seed_database()
