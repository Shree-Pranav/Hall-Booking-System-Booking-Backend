from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DATABASE_URL: str | None = None

    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    s = Settings()

    rebuild = False
    if not s.DATABASE_URL:
        rebuild = True
    else:
        lower_db_url = s.DATABASE_URL.lower()
        if ("localhost" in lower_db_url or "127.0.0.1" in lower_db_url) and s.DB_HOST and s.DB_HOST not in (
            "localhost",
            "127.0.0.1",
        ):
            rebuild = True

    if rebuild:
        s.DATABASE_URL = (
            f"postgresql+asyncpg://{s.DB_USER}:{s.DB_PASSWORD}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_NAME}"
        )

    return s


settings = get_settings()