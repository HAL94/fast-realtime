import redis
from sqlalchemy import create_engine
from app.core.config import AppSettings
from sqlalchemy.orm import sessionmaker, Session
from app.core.db.database import Base

def create_session_local():    
    settings = AppSettings()
    URL = f"postgresql://{settings.PG_USER}:{settings.PG_PW}@{settings.PG_SERVER}:{
        settings.PG_PORT
    }/{settings.PG_DB}"
    engine = create_engine(url=URL)
    Base.metadata.create_all(bind=engine)  # Create the table if it doesnt exist
    return sessionmaker(bind=engine)

        
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
    redis_password = None # If you have a password, fill it in

    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)
    redis_client.ping()  # Check if the connection is successful
    print("Redis connection successful.")

    return redis_client