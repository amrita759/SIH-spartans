import uuid
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.alert import Alert, AlertStatus
from app.schemas.alert import AlertOut
from app.schemas.common import APIResponse, PaginatedResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["Alert Engine"])


@router.get("", response_model=APIResponse[PaginatedResponse[AlertOut]])
async def list_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[AlertStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Alert)
    if status_filter:
        stmt = stmt.where(Alert.status == status_filter)

    res = await db.execute(stmt)
    alerts = res.scalars().all()
    total = len(alerts)

    stmt = stmt.order_by(Alert.created_at.desc()).offset((page - 1) * size).limit(size)
    res_page = await db.execute(stmt)
    items = res_page.scalars().all()

    pages = (total + size - 1) // size if total > 0 else 0
    return APIResponse(data=PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages))


@router.get("/{id}", response_model=APIResponse[AlertOut])
async def get_alert(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Alert).where(Alert.id == id)
    res = await db.execute(stmt)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return APIResponse(data=alert)


@router.post("/{id}/acknowledge", response_model=APIResponse[AlertOut])
async def acknowledge_alert(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Alert).where(Alert.id == id)
    res = await db.execute(stmt)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    return APIResponse(message="Alert acknowledged", data=alert)