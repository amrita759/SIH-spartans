import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintOut
from app.schemas.common import APIResponse, PaginatedResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/complaints", tags=["Cybercrime Complaints"])


@router.post("", response_model=APIResponse[ComplaintOut], status_code=status.HTTP_201_CREATED)
async def create_complaint(
    payload: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Complaint).where(Complaint.complaint_id == payload.complaint_id)
    res = await db.execute(query)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Complaint ID already exists")

    complaint = Complaint(**payload.model_dump())
    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)
    return APIResponse(message="Complaint record created successfully", data=complaint)


@router.get("", response_model=APIResponse[PaginatedResponse[ComplaintOut]])
async def list_complaints(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    state: Optional[str] = None,
    district: Optional[str] = None,
    crime_category: Optional[str] = None,
    status_filter: Optional[ComplaintStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Complaint)
    if state:
        stmt = stmt.where(Complaint.state.ilike(f"%{state}%"))
    if district:
        stmt = stmt.where(Complaint.district.ilike(f"%{district}%"))
    if crime_category:
        stmt = stmt.where(Complaint.crime_category.ilike(f"%{crime_category}%"))
    if status_filter:
        stmt = stmt.where(Complaint.status == status_filter)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    stmt = stmt.order_by(Complaint.complaint_datetime.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    items = result.scalars().all()

    pages = (total + size - 1) // size if total > 0 else 0

    paginated = PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)
    return APIResponse(message="Complaints retrieved", data=paginated)


@router.get("/{id}", response_model=APIResponse[ComplaintOut])
async def get_complaint(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Complaint).where(Complaint.id == id)
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return APIResponse(data=complaint)


@router.put("/{id}", response_model=APIResponse[ComplaintOut])
async def update_complaint(
    id: uuid.UUID,
    payload: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Complaint).where(Complaint.id == id)
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(complaint, field, val)

    await db.commit()
    await db.refresh(complaint)
    return APIResponse(message="Complaint updated successfully", data=complaint)


@router.delete("/{id}", response_model=APIResponse[dict])
async def delete_complaint(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Complaint).where(Complaint.id == id)
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    await db.delete(complaint)
    await db.commit()
    return APIResponse(message="Complaint deleted successfully", data={"id": str(id)})