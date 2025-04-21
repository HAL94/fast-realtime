import random
import redis
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.core.config import AppSettings
from sqlalchemy.orm import sessionmaker, Session
from app.core.db.database import Base
from app.core.db.models import User
from app.websocket.v1.scores.schema import PlayerRankAdd

settings = AppSettings()
URL = f"postgresql://{settings.PG_USER}:{settings.PG_PW}@{settings.PG_SERVER}:{
    settings.PG_PORT
}/{settings.PG_DB}"
engine = create_engine(url=URL)


def generate_leaderboard_data(
    players: list[User], game_channel: str
) -> list[PlayerRankAdd]:
    """Generates random leaderboard data."""

    leaderboard = []

    for rank, player in enumerate(players):
        game = game_channel
        score = random.randint(100, 1000)
        date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime(
            "%Y-%m-%d"
        )  # Random dates within the last 30 days.

        entry = PlayerRankAdd(
            user_id=player.id, player=player.name, game=game, score=score, date=date
        )

        leaderboard.append(entry)

    return leaderboard


def create_session_local():
    Base.metadata.create_all(bind=engine)  # Create the table if it doesnt exist
    return sessionmaker(bind=engine)


def clear_db():
    engine = create_engine(url=URL)
    SessionLocal = sessionmaker(bind=engine)

    db: Session = next(get_db(SessionLocal=SessionLocal))

    db.execute(text("DROP SCHEMA public CASCADE"))
    db.execute(text("CREATE SCHEMA public"))

    db.commit()
    Base.metadata.create_all(bind=engine)


def get_db(SessionLocal: sessionmaker[Session]):
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        print(f"an error occured: {e}")
    finally:
        db.close()


def create_redis_client():
    redis_host = "localhost"
    redis_port = 6379
    redis_db = 0
    redis_password = None  # If you have a password, fill it in

    redis_client = redis.Redis(
        host=redis_host, port=redis_port, db=redis_db, password=redis_password
    )
    try:
        redis_client.ping()  # Check if the connection is successful
        print("Redis connection successful.")
    except Exception as e:
        print(f"Redis connection failed: {e}")

    return redis_client
