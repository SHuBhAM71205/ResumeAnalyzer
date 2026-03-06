from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field

class Settings(BaseSettings):
    
    PROJECT_NAME: str = "AI Resume Analyzer"
    BACKEND_URL: str = "localhost"

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
    MINIO_ENDPOINT: str = "minio:9000"
    @computed_field
    def MINIO_EXTERNAL_URL(self) -> str:
        return f"http://{self.BACKEND_URL}:{self.MINIO_CLIENT_PORT}"

    # --- AI / VECTOR ---
    QDRANT_HOST: str = "qdrant"

    # REDIS
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_DB: int = 0
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


    #AUTH
    
    SECRETE_KEY:str
    HASH_ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    
    
    
    OPENAI_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    



settings = Settings()

