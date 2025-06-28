from celery import Celery  # type: ignore

from app.core.config.settings import settings

celery_app = Celery("morvo_ai", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_shutdown=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3500,  # 58 minutes
)

# Auto-discover tasks in the 'tasks' module of each app
celery_app.autodiscover_tasks(["app.tasks"])
