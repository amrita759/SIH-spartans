"""
backend/app/api/routes/alerts.py
Law Enforcement Alert dispatch, acknowledgment, and workflow endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.alert import AlertResponse, AlertAcknowledgeRequest
from backend.app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    status_filter: Optional[str] = Query(default=None, alias="status", description="NEW, ACKNOWLEDGED, UNDER_REVIEW, RESOLVED"),
    db: Session = Depends(get_db)
):
    """Retrieves high-risk predictive cash-out alerts."""
    return AlertService.get_alerts(db, status=status_filter)

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    """
    Acknowledges an active alert and transitions the associated cybercrime case into UNDER_REVIEW status.
    """
    updated = AlertService.acknowledge_alert(
        db=db,
        alert_id=alert_id,
        acknowledged_by=payload.acknowledged_by or "LEA_OFFICER"
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found."
        )
    return updated
