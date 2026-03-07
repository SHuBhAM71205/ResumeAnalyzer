from celery import shared_task
from qdrant_client import QdrantClient


from backend.Core.config import settings

qdrant_client = QdrantClient(url=settings.QDRANT_URL)

@shared_task
def compare_embeddings(resume_embedding, job_embedding):
    """
    Compare resume and job embeddings for similarity matching.
    
    Args:
        resume_embedding: Resume embedding vector
        job_embedding: Job description embedding vector
        
    Returns:
        float: Similarity score between 0 and 1
    """
    similarity_score = calculate_similarity(resume_embedding, job_embedding)
    return similarity_score


def calculate_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        float: Cosine similarity score
    """
    if not embedding1 or not embedding2:
        return 0.0
    
    # Cosine similarity calculation
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    norm1 = norm(embedding1)
    norm2 = norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def norm(embedding):
    """Calculate L2 norm of embedding vector."""
    return sum(x ** 2 for x in embedding) ** 0.5
