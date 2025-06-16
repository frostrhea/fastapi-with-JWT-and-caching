from pydantic_settings import BaseSettings
import dotenv


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    enable_cache: bool
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    class Config:
        env_file = "app/.env"


settings = Settings()