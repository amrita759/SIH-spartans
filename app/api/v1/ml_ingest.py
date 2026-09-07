import json
from datetime import datetime
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.workers.tasks import send_automated_alert

router = APIRouter(prefix="/internal/predictions", tags=["ML Engine"])


class PredictionPayload(BaseModel):
    zone_id: str
    latitude: float
    longitude: float
    risk_score: float
    confidence: float
    window_start: datetime
    window_end: datetime


@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest_prediction(
    payload: PredictionPayload,
    db: AsyncSession = Depends(get_db),
):
    # 1. Insert geospatial hotspot record into PostGIS
    stmt = text("""
        INSERT INTO hotspots (zone_id, center_point, risk_score, confidence, window_start, window_end)
        VALUES (
            :zone_id,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
            :risk,
            :conf,
            :w_start,
            :w_end
        )
    """)
    await db.execute(
        stmt,
        {
            "zone_id": payload.zone_id,
            "lat": payload.latitude,
            "lon": payload.longitude,
            "risk": payload.risk_score,
            "conf": payload.confidence,
            "w_start": payload.window_start,
            "w_end": payload.window_end,
        },
    )
    await db.commit()

    # 2. Trigger automated workflows for critical hotspots
    if payload.risk_score >= 0.75:
        # Offload webhook/SMS delivery to Celery worker
        send_automated_alert.delay(
            destination_webhook="https://example-bank.internal/alerts",
            alert_payload={
                "zone_id": payload.zone_id,
                "risk_score": payload.risk_score,
                "confidence": payload.confidence,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
            },
        )

        # Broadcast event to Redis Pub/Sub for live SSE subscribers
        redis_client = aioredis.from_url("redis://localhost:6379/0")
        await redis_client.publish(
            "crimesight_live_feed",
            json.dumps({
                "zone_id": payload.zone_id,
                "risk_score": payload.risk_score,
                "confidence": payload.confidence,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
            }),
        )
        await redis_client.close()

    return {"status": "ingested"}