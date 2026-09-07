import enum
from sqlalchemy import Column, String, Float, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.db.session import Base

from fastapi import APIRouter, Depends
from app.api.deps import require_roles
from app.models.schema import UserRole

router = APIRouter()

@router.get("/hotspots/secure")
async def get_secure_hotspots(
    current_user: dict = Depends(require_roles([UserRole.LEA_OFFICER, UserRole.I4C_ADMIN]))
):
    return {"message": "Access granted", "user": current_user}

class UserRole(str, enum.Enum):
    LEA_OFFICER = "LEA_OFFICER"
    BANK_FI_USER = "BANK_FI_USER"
    I4C_ADMIN = "I4C_ADMIN"

class Hotspot(Base):
    __tablename__ = "hotspots"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    zone_id = Column(String(50), nullable=False)
    center_point = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    risk_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)