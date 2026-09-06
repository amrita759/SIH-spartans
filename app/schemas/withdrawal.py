import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class WithdrawalCreate(BaseModel):
    withdrawal_id: str
    transaction_id: Optional[uuid.UUID] = None
    atm_id: str
    amount: float
    withdrawal_datetime: datetime
    latitude: float
    longitude: float
    state: str
    district: str


class WithdrawalOut(BaseModel):
    id: uuid.UUID
    withdrawal_id: str
    transaction_id: Optional[uuid.UUID] = None
    atm_id: str
    amount: float
    withdrawal_datetime: datetime
    latitude: float
    longitude: float
    state: str
    district: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)