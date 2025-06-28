from celery import Celery  # type: ignore
from celery.signals import task_prerun, task_postrun, task_failure  # type: ignore
import time

from app.core.config.settings import settings
from app.core.metrics import TASK_DURATION_SECONDS, TASKS_TOTAL

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

# ---------------------------------------------------------------------------
# Prometheus metrics hooks
# ---------------------------------------------------------------------------

@task_prerun.connect
def _task_start_handler(task_id, task, **kwargs):  # type: ignore[override]
    task.request.__dict__["_start_time"] = time.perf_counter()

@task_postrun.connect
def _task_postrun_handler(task_id, task, retval, state, **kwargs):  # type: ignore[override]
    start = task.request.__dict__.pop("_start_time", None)
    if start is not None:
        duration = time.perf_counter() - start
        TASK_DURATION_SECONDS.labels(task_name=task.name).observe(duration)
    TASKS_TOTAL.labels(task_name=task.name, status="success").inc()

@task_failure.connect
def _task_failure_handler(task_id, exception, task, **kwargs):  # type: ignore[override]
    TASKS_TOTAL.labels(task_name=task.name, status="failure").inc()
