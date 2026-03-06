from minio import Minio
from backend.Core.config import settings


Minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key= settings.MINIO_ROOT_USER,
    secret_key= settings.MINIO_ROOT_USER,
    secure=False
)

