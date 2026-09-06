from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.complaint import Complaint
from app.models.alert import Alert, AlertStatus
from app.models.prediction import Prediction, RiskLevel
from app.schemas.common import APIResponse
from app.schemas.analytics import DashboardSummary
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard Statistics"])


@router.get("/summary", response_model=APIResponse[DashboardSummary])
async def get_dashboard_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    c_stmt = select(func.count(Complaint.id), func.coalesce(func.sum(Complaint.fraud_amount), 0.0))
    c_res = await db.execute(c_stmt)
    c_count, total_fraud = c_res.one()

    a_stmt = select(func.count(Alert.id)).where(Alert.status == AlertStatus.UNACKNOWLEDGED)
    a_res = await db.execute(a_stmt)
    active_alerts = a_res.scalar() or 0

    p_stmt = select(func.count(Prediction.id)).where(Prediction.risk_level == RiskLevel.CRITICAL)
    p_res = await db.execute(p_stmt)
    critical_hotspots = p_res.scalar() or 0

    summary = DashboardSummary(
        total_complaints=c_count,
        total_fraud_amount=float(total_fraud),
        active_alerts=active_alerts,
        critical_hotspots=critical_hotspots
    )
    return APIResponse(data=summary)


@router.get("/risk-trends", response_model=APIResponse[dict])
async def get_risk_trends(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return APIResponse(data={
        "trends": [
            {"date": "2026-09-01", "complaints": 12, "high_risk_predictions": 3},
            {"date": "2026-09-02", "complaints": 18, "high_risk_predictions": 5},
            {"date": "2026-09-03", "complaints": 25, "high_risk_predictions": 8},
            {"date": "2026-09-04", "complaints": 15, "high_risk_predictions": 4},
            {"date": "2026-09-05", "complaints": 30, "high_risk_predictions": 11}
        ]
    })


@router.get("/top-hotspots", response_model=APIResponse[dict])
async def get_top_hotspots(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Prediction).where(Prediction.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])).limit(5)
    res = await db.execute(stmt)
    top_preds = res.scalars().all()
    out = [{
        "latitude": p.latitude,
        "longitude": p.longitude,
        "risk_score": p.risk_score,
        "risk_level": p.risk_level.value
    } for p in top_preds]
    return APIResponse(data={"hotspots": out})