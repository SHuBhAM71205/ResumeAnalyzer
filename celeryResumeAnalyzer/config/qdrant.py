from qdrant_client import QdrantClient

from backend.Core.config import settings

def get_qdrant_client():

    return QdrantClient(
        url=settings.QDRANT_URL,
    )