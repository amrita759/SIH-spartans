import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.alert import AlertSeverity, AlertStatus
from app.models.user import UserRole


class AlertOut(BaseModel):
    id: uuid.UUID
    prediction_id: uuid.UUID
    alert_type: str
    severity: AlertSeverity
    recipient_role: UserRole
    message: str
    status: AlertStatus
    created_at: datetime
    acknowledged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)