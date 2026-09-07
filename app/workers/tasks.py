import requests
from app.workers.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def send_automated_alert(self, destination_webhook: str, alert_payload: dict):
    try:
        response = requests.post(destination_webhook, json=alert_payload, timeout=5)
        response.raise_for_status()
        return {"status": "dispatched", "status_code": response.status_code}
    except Exception as exc:
        # Exponential backoff or static retry delay (10s)
        raise self.retry(exc=exc, countdown=10)
    