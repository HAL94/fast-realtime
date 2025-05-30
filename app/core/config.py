# import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# ------------- database ------------
class PostgresSettings(BaseSettings):
    PG_USER: str
    PG_PW: str
    PG_SERVER: str
    PG_PORT: str
    PG_DB: str

class JwtSettings(BaseSettings):
    SECRET_KEY: str = "a5f1e06590c961d334e7a8e632712d984439fc43bad6ccdb977446579bd82e4a"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 60.0


class AppSettings(PostgresSettings, JwtSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')


settings = AppSettings()

def get_settings():
    return settings
