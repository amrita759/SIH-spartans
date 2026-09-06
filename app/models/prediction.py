import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    alerts = relationship("Alert", back_populates="prediction", cascade="all, delete-orphan")