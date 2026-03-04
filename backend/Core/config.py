from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field

class Settings(BaseSettings):
    
    PROJECT_NAME: str = "AI Resume Analyzer"
    BACKEND_URL: str = "localhost"

    PG_DB_NAME: str
    PG_DB_USER: str
    PG_DB_PASSWORD: str
    
    @computed_field
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PG_DB_USER}:{self.PG_DB_PASSWORD}@db:5432/{self.PG_DB_NAME}"

    # --- MINIO ---
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_CLIENT_PORT: int = 9000
    
    # Internal DNS for Docker
    MINIO_ENDPOINT: str = "minio:9000"
    
    @computed_field
    def MINIO_EXTERNAL_URL(self) -> str:
        return f"http://{self.BACKEND_URL}:{self.MINIO_CLIENT_PORT}"

    # --- AI / VECTOR ---
    OPENAI_API_KEY: str
    QDRANT_HOST: str = "qdrant"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # REDIS

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

# Initialize it once
settings = Settings()


if __name__ == "__main__":
    
    print(settings.OPEN)