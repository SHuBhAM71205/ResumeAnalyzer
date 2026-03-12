from celery import Celery
from backend.Core.config import settings


def make_celery(app=None):
    celery = Celery('resume_analyzer')
    
    # Configure from settings
    celery.conf.update(
        broker_url=settings.CELERY_BROKER_URL,
        result_backend=settings.CELERY_RESULT_BACKEND,
        accept_content=settings.CELERY_ACCEPT_CONTENT,
        task_serializer=settings.CELERY_TASK_SERIALIZER,
        result_serializer=settings.CELERY_RESULT_SERIALIZER,
        timezone=settings.CELERY_TIMEZONE,
    )
    
    if app:
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


class CeleryConfig:
    """Celery configuration class for direct use"""
    broker_url = settings.CELERY_BROKER_URL
    result_backend = settings.CELERY_RESULT_BACKEND
    accept_content = [settings.CELERY_ACCEPT_CONTENT]
    task_serializer = settings.CELERY_TASK_SERIALIZER
    result_serializer = settings.CELERY_RESULT_SERIALIZER
    timezone = settings.CELERY_TIMEZONE

