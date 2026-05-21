from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DATABASE_URL: str

    SECRET_KEY: str = "7Yw4gC1fQp2zLk9XvN8mRsT6uHaJd3BeW0nPy5EtUi"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """
        Automatically construct DATABASE_URL if:
        - it is missing
        - OR it incorrectly points to localhost while DB_HOST is something else
        """

        rebuild = False

        if not self.DATABASE_URL:
            rebuild = True
        else:
            lower_db_url = self.DATABASE_URL.lower()

            if (
                ("localhost" in lower_db_url or "127.0.0.1" in lower_db_url)
                and self.DB_HOST not in ("localhost", "127.0.0.1")
            ):
                rebuild = True

        if rebuild:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://"
                f"{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
