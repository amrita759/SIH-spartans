from celery import Celery

celery_app = Celery(
    "crimesight_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

# Auto-discover tasks in app.workers.tasks
celery_app.autodiscover_tasks(["app.workers"])