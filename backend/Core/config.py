from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field

class Settings(BaseSettings):
    
    PROJECT_NAME: str = "AI Resume Analyzer"
    BACKEND_URL: str = "localhost"
    APP_PORT: int = 8000

    #--- POSTGRES---
    PG_DB_NAME: str
    PG_DB_USER: str
    PG_DB_PASSWORD: str
    PG_DB_HOST: str = "localhost"
    PG_DB_PORT: int = 5432
    
    @computed_field
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PG_DB_USER}:{self.PG_DB_PASSWORD}@{self.PG_DB_HOST}:{self.PG_DB_PORT}/{self.PG_DB_NAME}"

    # --- MINIO ---
    MINIO_CLIENT_PORT: int = 9000
    MINIO_UI_PORT: int = 9000
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_BUCKET_NAME: str = "resume"
    @computed_field
    def MINIO_EXTERNAL_URL(self) -> str:
        return f"http://{self.BACKEND_URL}:{self.MINIO_CLIENT_PORT}"

    # --- AI / VECTOR ---
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    
    @computed_field
    def QDRANT_URL(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"

    # REDIS (Backend Caching & Rate Limiting)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # REDIS (Celery - Separate Instance)
    CELERY_REDIS_HOST: str = "redis-celery"
    CELERY_REDIS_PORT: int = 6380
    CELERY_REDIS_PASSWORD: str = ""
    CELERY_REDIS_DB_BROKER: int = 0
    CELERY_REDIS_DB_BACKEND: int = 1

    @property
    def CELERY_BROKER_URL(self) -> str:
        if self.CELERY_REDIS_PASSWORD:
            return f"redis://:{self.CELERY_REDIS_PASSWORD}@{self.CELERY_REDIS_HOST}:{self.CELERY_REDIS_PORT}/{self.CELERY_REDIS_DB_BROKER}"
        return f"redis://{self.CELERY_REDIS_HOST}:{self.CELERY_REDIS_PORT}/{self.CELERY_REDIS_DB_BROKER}"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        if self.CELERY_REDIS_PASSWORD:
            return f"redis://:{self.CELERY_REDIS_PASSWORD}@{self.CELERY_REDIS_HOST}:{self.CELERY_REDIS_PORT}/{self.CELERY_REDIS_DB_BACKEND}"
        return f"redis://{self.CELERY_REDIS_HOST}:{self.CELERY_REDIS_PORT}/{self.CELERY_REDIS_DB_BACKEND}"

    # CELERY
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_TIMEZONE: str = "UTC"

    # AUTH
    SECRETE_KEY: str
    HASH_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # AI / API
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_ENDPOINT: str = "https://api.openai.com/v1/embeddings"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # LIMITS
    GLOBAL_RATE_LIMIT_PER_MINUTE: int = 100  # Max requests per minute per IP
    AUTH_RATE_LIMIT_PER_MINUTE: int = 5      # Max Auth request in a min allow per IP
    RESUME_UPLOAD_LIMIT: int = 10             # Max Resume upload in a min allow per userid

settings = Settings()  # type:ignore

