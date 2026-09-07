import io
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.models.transaction import FinancialTransaction
from app.models.withdrawal import Withdrawal
from app.schemas.common import APIResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/data/import", tags=["Bulk Data Ingestion"])


@router.post("/complaints", response_model=APIResponse[dict])
async def import_complaints(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files supported")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    required_cols = ["complaint_id", "crime_category", "fraud_amount", "complaint_datetime", "state", "district", "latitude", "longitude"]
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required CSV column: {col}")

    df = df.dropna(subset=required_cols)
    df = df[(df["latitude"].between(6.0, 37.5)) & (df["longitude"].between(68.5, 97.5))]

    inserted = 0
    for _, row in df.iterrows():
        c_id = str(row["complaint_id"]).strip()
        stmt = select(Complaint).where(Complaint.complaint_id == c_id)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            continue

        complaint = Complaint(
            complaint_id=c_id,
            crime_category=str(row["crime_category"]),
            description=str(row.get("description", "")) if pd.notna(row.get("description")) else None,
            fraud_amount=float(row["fraud_amount"]),
            complaint_datetime=pd.to_datetime(row["complaint_datetime"]).to_pydatetime(),
            state=str(row["state"]),
            district=str(row["district"]),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            status=ComplaintStatus.PENDING
        )
        db.add(complaint)
        inserted += 1

    await db.commit()
    return APIResponse(message=f"Successfully imported {inserted} complaint records", data={"inserted_count": inserted})


@router.post("/transactions", response_model=APIResponse[dict])
async def import_transactions(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files supported")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    required_cols = ["transaction_id", "transaction_type", "amount", "transaction_datetime", "source_location", "destination_location", "bank_name", "account_reference"]
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required CSV column: {col}")

    df = df.dropna(subset=required_cols)
    inserted = 0
    for _, row in df.iterrows():
        tx_id = str(row["transaction_id"]).strip()
        stmt = select(FinancialTransaction).where(FinancialTransaction.transaction_id == tx_id)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            continue

        tx = FinancialTransaction(
            transaction_id=tx_id,
            transaction_type=str(row["transaction_type"]),
            amount=float(row["amount"]),
            transaction_datetime=pd.to_datetime(row["transaction_datetime"]).to_pydatetime(),
            source_location=str(row["source_location"]),
            destination_location=str(row["destination_location"]),
            bank_name=str(row["bank_name"]),
            account_reference=str(row["account_reference"])
        )
        db.add(tx)
        inserted += 1

    await db.commit()
    return APIResponse(message=f"Successfully imported {inserted} transaction records", data={"inserted_count": inserted})


@router.post("/withdrawals", response_model=APIResponse[dict])
async def import_withdrawals(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files supported")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    required_cols = ["withdrawal_id", "atm_id", "amount", "withdrawal_datetime", "latitude", "longitude", "state", "district"]
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required CSV column: {col}")

    df = df.dropna(subset=required_cols)
    df = df[(df["latitude"].between(6.0, 37.5)) & (df["longitude"].between(68.5, 97.5))]

    inserted = 0
    for _, row in df.iterrows():
        w_id = str(row["withdrawal_id"]).strip()
        stmt = select(Withdrawal).where(Withdrawal.withdrawal_id == w_id)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            continue

        w = Withdrawal(
            withdrawal_id=w_id,
            atm_id=str(row["atm_id"]),
            amount=float(row["amount"]),
            withdrawal_datetime=pd.to_datetime(row["withdrawal_datetime"]).to_pydatetime(),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            state=str(row["state"]),
            district=str(row["district"])
        )
        db.add(w)
        inserted += 1

    await db.commit()
    return APIResponse(message=f"Successfully imported {inserted} cash withdrawal records", data={"inserted_count": inserted})