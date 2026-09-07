
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(prefix="/hotspots", tags=["Hotspots"])

@router.get("/geojson")
async def get_geojson_heatmap(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', coalesce(json_agg(ST_AsGeoJSON(t.*)::json), '[]'::json)
        )
        FROM (
            SELECT id, zone_id, risk_score, center_point AS geometry
            FROM hotspots
            WHERE center_point && ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
        ) AS t;
    """)
    result = await db.execute(query, {
        "min_lon": min_lon,
        "min_lat": min_lat,
        "max_lon": max_lon,
        "max_lat": max_lat
    })
    return result.scalar()
