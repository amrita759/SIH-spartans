import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.withdrawal import Withdrawal
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalOut
from app.schemas.common import APIResponse, PaginatedResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/withdrawals", tags=["Cash Withdrawals"])


@router.post("", response_model=APIResponse[WithdrawalOut], status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    payload: WithdrawalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Withdrawal).where(Withdrawal.withdrawal_id == payload.withdrawal_id)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Withdrawal ID already exists")

    w = Withdrawal(**payload.model_dump())
    db.add(w)
    await db.commit()
    await db.refresh(w)
    return APIResponse(message="Cash withdrawal logged", data=w)


@router.get("", response_model=APIResponse[PaginatedResponse[WithdrawalOut]])
async def list_withdrawals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    state: Optional[str] = None,
    district: Optional[str] = None,
    atm_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Withdrawal)
    if state:
        stmt = stmt.where(Withdrawal.state.ilike(f"%{state}%"))
    if district:
        stmt = stmt.where(Withdrawal.district.ilike(f"%{district}%"))
    if atm_id:
        stmt = stmt.where(Withdrawal.atm_id == atm_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    stmt = stmt.order_by(Withdrawal.withdrawal_datetime.desc()).offset((page - 1) * size).limit(size)
    res = await db.execute(stmt)
    items = res.scalars().all()

    pages = (total + size - 1) // size if total > 0 else 0
    return APIResponse(data=PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages))


@router.get("/{id}", response_model=APIResponse[WithdrawalOut])
async def get_withdrawal(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Withdrawal).where(Withdrawal.id == id)
    res = await db.execute(stmt)
    w = res.scalar_one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Withdrawal record not found")
    return APIResponse(data=w)