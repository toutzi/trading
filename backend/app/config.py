from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./dev.db"
    jwt_secret: str = "dev-only-secret-change-me-in-prod-0123456789abcdef"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15


settings = Settings()
