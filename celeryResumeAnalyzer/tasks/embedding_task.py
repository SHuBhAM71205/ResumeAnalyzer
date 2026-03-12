from celery import shared_task
import json
import redis
import pymupdf

from backend.Core.config import settings
from celeryResumeAnalyzer.EmbeddingModel.BERT import get_embedding

from celeryResumeAnalyzer.config.qdrant import get_qdrant_client
from qdrant_client.models import PointStruct

from backend.Core.minio import Minio_client
# Initialize Redis client for caching embeddings
def get_redis_embedding_cache():
    """Get Redis client for embedding cache"""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )

def pdf_to_text(resume_obj):
    
    doc= pymupdf.open(stream=resume_obj,filetype="pdf")

    full_text:str = ""
    
    for page in doc:
        full_text+=page.get_text()
    
    return full_text

@shared_task(bind=True, max_retries=3)
def store_resume_embedding(self, minio_path):
    try:
        print(Minio_client._endpoint_url)
        response = Minio_client.get_object(settings.MINIO_BUCKET_NAME, minio_path)
        
        resume_bytes = response.read()
        response.close()
        response.release_conn()
        
        text = pdf_to_text(resume_bytes)
        
        id = minio_path.split("/")[0] 
        
        cache_key = f"embedding:{id}"
        
        redis_client = get_redis_embedding_cache()
        cached_embedding = redis_client.get(cache_key)
        
        if cached_embedding:
            return {
                "status": "success",
                "source": "cache",
                "embedding": json.loads(cached_embedding)
            }
            
        embedding = get_embedding(text)
        if hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()

        qudrant_client = get_qdrant_client()
        
        qudrant_client.upsert(
            collection_name="resumes",
            points=[
                PointStruct(
                    id=id,
                    vector=embedding,
                    payload={"text": text, "minio_path": minio_path}
                )
            ]
        )

        redis_client.set(cache_key, json.dumps(embedding), ex=60*60*24)
        
        return {
            "status": "success",
            "source": "Qdrant",
            "embedding": embedding
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=20)
    