from minio import Minio
from backend.Core.config import settings
from urllib3 import PoolManager,Retry

http_client = PoolManager(
    retries=Retry(
        total=5,
        backoff_factor=0.2,
        status_forcelist=[500, 502, 503, 504],
    ),
    maxsize=10, # Number of connections to keep in the pool
)


Minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key= settings.MINIO_ROOT_USER,
    secret_key= settings.MINIO_ROOT_PASSWORD,
    secure=False,
    http_client=http_client
)


if not Minio_client.bucket_exists("resume"):
    try:
        Minio_client.make_bucket("resume")
        print(f"Created the bucket `resume`")

    except Exception as e:
        print(f"Unable to create the bucket in minio")
