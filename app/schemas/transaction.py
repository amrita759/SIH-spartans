import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    transaction_id: str
    complaint_id: Optional[uuid.UUID] = None
    transaction_type: str
    amount: float
    transaction_datetime: datetime
    source_location: str
    destination_location: str
    bank_name: str
    account_reference: str


class TransactionOut(BaseModel):
    id: uuid.UUID
    transaction_id: str
    complaint_id: Optional[uuid.UUID] = None
    transaction_type: str
    amount: float
    transaction_datetime: datetime
    source_location: str
    destination_location: str
    bank_name: str
    account_reference: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)