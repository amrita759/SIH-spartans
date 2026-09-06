import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.transaction import FinancialTransaction
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.schemas.common import APIResponse, PaginatedResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/transactions", tags=["Financial Transactions"])


@router.post("", response_model=APIResponse[TransactionOut], status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(FinancialTransaction).where(FinancialTransaction.transaction_id == payload.transaction_id)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Transaction ID already exists")

    tx = FinancialTransaction(**payload.model_dump())
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return APIResponse(message="Financial transaction recorded", data=tx)


@router.get("", response_model=APIResponse[PaginatedResponse[TransactionOut]])
async def list_transactions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    bank_name: Optional[str] = None,
    transaction_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(FinancialTransaction)
    if bank_name:
        stmt = stmt.where(FinancialTransaction.bank_name.ilike(f"%{bank_name}%"))
    if transaction_type:
        stmt = stmt.where(FinancialTransaction.transaction_type == transaction_type)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    stmt = stmt.order_by(FinancialTransaction.transaction_datetime.desc()).offset((page - 1) * size).limit(size)
    res = await db.execute(stmt)
    items = res.scalars().all()

    pages = (total + size - 1) // size if total > 0 else 0
    return APIResponse(data=PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages))


@router.get("/{id}", response_model=APIResponse[TransactionOut])
async def get_transaction(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(FinancialTransaction).where(FinancialTransaction.id == id)
    res = await db.execute(stmt)
    tx = res.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return APIResponse(data=tx)