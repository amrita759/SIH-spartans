import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ComplaintStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    complaint_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    crime_category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    fraud_amount: Mapped[float] = mapped_column(Float, nullable=False)
    complaint_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(SQLEnum(ComplaintStatus), default=ComplaintStatus.PENDING, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    transactions = relationship("FinancialTransaction", back_populates="complaint", cascade="all, delete-orphan")