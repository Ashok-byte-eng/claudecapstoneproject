from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://capstone:capstone@localhost:5432/capstone"
    redis_url: str = "redis://localhost:6379"
    allowed_origins: list[str] = ["http://localhost:3000"]
    applicationinsights_connection_string: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
