import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.withdrawal import Withdrawal
from app.models.prediction import Prediction, RiskLevel
from app.geospatial.clusterer import detect_withdrawal_hotspots
from app.geospatial.heatmap import generate_geojson_heatmap
from app.schemas.analytics import HotspotOut
from app.schemas.common import APIResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["Geospatial & Analytics"])


@router.get("/analytics/hotspots", response_model=APIResponse[List[HotspotOut]])
async def get_hotspots(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Withdrawal)
    res = await db.execute(stmt)
    withdrawals = res.scalars().all()

    if not withdrawals:
        return APIResponse(message="No data available for spatial clustering", data=[])

    data = [{
        "withdrawal_id": str(w.withdrawal_id),
        "latitude": w.latitude,
        "longitude": w.longitude,
        "amount": w.amount
    } for w in withdrawals]

    df = pd.DataFrame(data)
    clusters = detect_withdrawal_hotspots(df)
    if clusters.empty:
        return APIResponse(message="No clusters found", data=[])

    out = clusters.to_dict(orient="records")
    return APIResponse(data=out)


@router.get("/map/risk-heatmap", response_model=APIResponse[dict])
async def get_risk_heatmap(
    risk_level: Optional[RiskLevel] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Prediction)
    if risk_level:
        stmt = stmt.where(Prediction.risk_level == risk_level)

    res = await db.execute(stmt)
    predictions = res.scalars().all()

    preds_data = [{
        "latitude": p.latitude,
        "longitude": p.longitude,
        "risk_score": p.risk_score,
        "risk_level": p.risk_level.value,
        "confidence": p.confidence,
        "predicted_time": p.predicted_time
    } for p in predictions]

    geojson = generate_geojson_heatmap(preds_data)
    return APIResponse(data=geojson)