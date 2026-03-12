from celery import Celery
import os

from celeryResumeAnalyzer.config.celery_config import CeleryConfig

celery_app = Celery('resume_analyzer')
celery_app.config_from_object(CeleryConfig)
celery_app.set_default()


celery_app.autodiscover_tasks([
    'celeryResumeAnalyzer.tasks'
])

