# Prometheus metrics for Celery tasks
from prometheus_client import Counter, Histogram

TASK_DURATION_SECONDS = Histogram(
    "celery_task_duration_seconds",
    "Time spent executing Celery tasks",
    ["task_name"],
)

TASKS_TOTAL = Counter(
    "celery_tasks_total",
    "Total number of Celery tasks executed",
    ["task_name", "status"],
) 