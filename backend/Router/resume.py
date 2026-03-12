from fastapi.routing import APIRouter
from fastapi import Depends, UploadFile,BackgroundTasks,HTTPException
from fastapi.responses import StreamingResponse

from uuid import uuid4,UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.Middleware.limmiter import resume_rate_limiter
from backend.Service.auth import get_current_user
from backend.Service.resume import save_to_minio
from backend.Model.model import Resume, User
from backend.Core.db import get_db
from backend.Core.config import settings

from backend.Middleware.redis_cache import (
    redis_cache_invalidate,
    redis_resume_cache_get,
    redis_resume_cache_set,
)
from backend.Core.minio import Minio_client

from celeryResumeAnalyzer.celery import celery_app

router = APIRouter(
    prefix="/resume",
    tags=["resume"]
)

@router.get(
    "/{user_id}",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF file of the resume"
        },
        404: {"description": "Resume not found"}
    }
)
async def get_resume(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a resume PDF by user ID.
    
    Returns the stored resume as a PDF file. Results are cached in Redis for 1 minute.
    """
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only access your own resume")

    # Try to get from cache first
    cached_resume = await redis_resume_cache_get(user_id)
    if cached_resume:
        return StreamingResponse(iter([cached_resume]), media_type="application/pdf")
    
    # Cache miss - fetch from database and MinIO
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Fetch from MinIO
    resume_obj = Minio_client.get_object(settings.MINIO_BUCKET_NAME, resume.minio_object_name)
    resume_data = resume_obj.read()
    
    # Cache the resume data for future requests
    await redis_resume_cache_set(user_id, resume_data)
    
    return StreamingResponse(iter([resume_data]), media_type="application/pdf")


@router.post(
    "/upload/{user_id}",
    dependencies=[Depends(resume_rate_limiter)],
    responses={
        200: {"description": "Resume uploaded successfully"},
        400: {"description": "Invalid file type"},
        429: {"description": "Rate limit exceeded"}
    }
)
async def resume_upload_user(
    user_id: UUID,
    file: UploadFile,
    background_task: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a resume PDF for a specific user.
    
    Accepts only PDF files. The file is processed in the background.
    Returns the resume ID for future reference.
    """
    
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only upload your own resume")

    if file.content_type != "application/pdf": 
        raise HTTPException(status_code=400,detail="Only PDF type allowed for resume")
    
    file_extension = file.filename.split(".")[-1] # type: ignore
    
    unique_filename = f"{user_id}/{uuid4()}.{file_extension}"    
    
    file_size = len(await file.read())
    await file.seek(0)
    
    new_resume = Resume(
        
        user_id=user_id,
        minio_object_name=unique_filename,
        file_size=file_size,
        status="processing",
        
    )
    
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)

    await redis_cache_invalidate(f"resume_cache:{user_id}")
    
    background_task.add_task(save_to_minio, settings.MINIO_BUCKET_NAME, unique_filename, file.file)

    try:
        celery_app.send_task(
            "celeryResumeAnalyzer.tasks.embedding_task.store_resume_embedding",
            args=[unique_filename],
        )
    except Exception as exc:
        print(f"Unable to queue embedding task for {unique_filename}: {exc}")
    
    
    return {
        "message": "Resume uploaded successfully",
        "resume_id": new_resume.id
    }



@router.post(
    "/analyze/{resume_id}",
    responses={
        200: {"description": "Resume analysis completed"},
        404: {"description": "Resume not found"}
    }
)
async def resume_analyze(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze a resume using AI/RAG system.
    
    Performs analysis on the stored resume including job matching,
    skill extraction, and recommendations.
    """
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only analyze your own resume")
    
    # TODO: Implement resume analysis logic
    return {"message": "Resume analysis feature coming soon"}



@router.put(
    "/update/{resume_id}",
    responses={
        200: {"description": "Resume updated successfully"},
        400: {"description": "Invalid file type"},
        404: {"description": "Resume not found"}
    }
)
async def resume_update(
    resume_id: UUID,
    file: UploadFile,
    background_task: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing resume for a user.
    
    Accepts only PDF files. The file is processed in the background,
    replacing the previous version.
    """
    if file.content_type != "application/pdf": 
        raise HTTPException(status_code=400, detail="Only PDF type allowed for resume")
    
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own resume")
    
    file_size = len(await file.read())
    await file.seek(0)
    
    resume.file_size = file_size
    resume.status = "processing"
    
    await db.commit()

    await redis_cache_invalidate(f"resume_cache:{resume.user_id}")
    
    background_task.add_task(save_to_minio, settings.MINIO_BUCKET_NAME, resume.minio_object_name, file.file)
    
    return {
        "message": "Resume updated successfully",
        "resume_id": resume.id
    }

