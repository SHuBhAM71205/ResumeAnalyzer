from celery import shared_task
import requests
import sys
import os
import json
import hashlib
import redis

# Add the backend path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.Core.config import settings

# Initialize Redis client for caching embeddings
def get_redis_embedding_cache():
    """Get Redis client for embedding cache"""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )


@shared_task(bind=True, max_retries=3)
def store_resume_embedding(self, resume_data):
    """
    Generate and store embedding for resume data.
    Uses Redis cache to avoid duplicate API calls for the same content.
    
    Args:
        resume_data: Resume text content
        
    Returns:
        dict: Embedding vector and metadata
    """
    try:
        # Create hash of resume data to use as cache key
        data_hash = hashlib.md5(resume_data.encode()).hexdigest()
        cache_key = f"embedding:{data_hash}"
        
        # Check if embedding already exists in cache
        redis_client = get_redis_embedding_cache()
        cached_embedding = redis_client.get(cache_key)
        
        if cached_embedding:
            return {
                "status": "success",
                "source": "cache",
                "embedding": json.loads(cached_embedding)
            }
        
        # Call OpenAI API to generate embedding
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": resume_data,
            "model": settings.EMBEDDING_MODEL
        }
        
        response = requests.post(
            settings.EMBEDDING_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            embedding_data = response.json()
            embedding_vector = embedding_data.get("data", [{}])[0].get("embedding")
            
            if not embedding_vector:
                raise ValueError("No embedding vector in API response")
            
            # Cache the embedding for 24 hours (86400 seconds)
            redis_client.setex(
                cache_key,
                86400,
                json.dumps(embedding_vector)
            )
            
            return {
                "status": "success",
                "source": "api",
                "embedding": embedding_vector
            }
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        # Retry on network errors
        raise self.retry(exc=e, countdown=60)
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
