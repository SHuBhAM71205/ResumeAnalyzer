from celery import Celery
import os

from config.celery_config import CeleryConfig

celery_app = Celery('resume_analyzer')
celery_app.config_from_object(CeleryConfig)


celery_app.autodiscover_tasks(['tasks.embedding_tasks', 'tasks.comparison_tasks'])