import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.report import IntelligenceReport
from app.schemas.report import ReportCreate, ReportOut
from app.schemas.common import APIResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports/intelligence", tags=["Intelligence Reports"])


@router.post("", response_model=APIResponse[ReportOut], status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = IntelligenceReport(
        title=payload.title,
        summary=payload.summary,
        risk_level=payload.risk_level,
        risk_score=payload.risk_score,
        latitude=payload.latitude,
        longitude=payload.longitude,
        predicted_locations=payload.predicted_locations,
        related_complaints=payload.related_complaints,
        related_transactions=payload.related_transactions,
        recommended_action=payload.recommended_action,
        created_by=current_user.id
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return APIResponse(message="Intelligence report generated", data=report)


@router.get("", response_model=APIResponse[List[ReportOut]])
async def list_reports(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(IntelligenceReport).order_by(IntelligenceReport.created_at.desc())
    res = await db.execute(stmt)
    reports = res.scalars().all()
    return APIResponse(data=reports)


@router.get("/{id}", response_model=APIResponse[ReportOut])
async def get_report(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(IntelligenceReport).where(IntelligenceReport.id == id)
    res = await db.execute(stmt)
    report = res.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Intelligence report not found")
    return APIResponse(data=report)