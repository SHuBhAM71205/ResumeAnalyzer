from backend.Core.db import SessionLocal
from backend.Core.minio import Minio_client
from backend.Core.config import settings
from backend.Model.model import Resume

from sqlalchemy import update

async def save_to_minio(bucket_name:str, object_name:str, Data):
    
    try:
        Minio_client.put_object(
            bucket_name,
            object_name,
            Data,
            length=-1,
            part_size=10*1024*1024 
        )
        
        
        resume_status = "completed"
        async with SessionLocal() as db:
            stmt = update(Resume).where(Resume.minio_object_name == object_name).values(status=resume_status)
            await db.execute(stmt)
            await db.commit()
        
        
        print(f"File {object_name} uploaded successfully to bucket {bucket_name}")
    
    except Exception as e:
        print(f"Error uploading file to Minio: {e}")

