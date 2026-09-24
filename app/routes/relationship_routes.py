"""Consultas de historial por usuario y dispositivo."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.dependencies.database_dependency import database_session
from app.dependencies.auth_dependency import require_support
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanDetailResponse
from app.services.loan_service import to_detail

router = APIRouter(tags=["Loans"])


@router.get("/users/{user_id}/loans", response_model=list[LoanDetailResponse])
async def get_user_loans(
    user_id: int,
    db: Session = Depends(database_session),
    _current_user=Depends(require_support),
):
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    query = (
        select(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .where(Loan.user_id == user_id)
        .order_by(Loan.loan_date.desc())
    )
    return [to_detail(loan) for loan in db.scalars(query).unique().all()]


@router.get("/devices/{device_id}/loans", response_model=list[LoanDetailResponse])
async def get_device_loans(
    device_id: int,
    db: Session = Depends(database_session),
    _current_user=Depends(require_support),
):
    if db.get(Device, device_id) is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    query = (
        select(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .where(Loan.device_id == device_id)
        .order_by(Loan.loan_date.desc())
    )
    return [to_detail(loan) for loan in db.scalars(query).unique().all()]
