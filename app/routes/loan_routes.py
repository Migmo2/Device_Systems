"""Endpoints de prestamos, devoluciones y consultas con joins."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import database_session
from app.dependencies.auth_dependency import get_current_active_user, require_support
from app.core.rate_limit import limiter
from app.models.device_model import Device
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse, LoanStatus
from app.services.loan_service import create_loan, get_loan, list_loans, return_loan, to_detail

router = APIRouter(prefix="/loans", tags=["Loans"])


def require_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def require_device(db: Session, device_id: int) -> Device:
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device


@router.get("", response_model=list[LoanResponse], summary="Listar prestamos")
async def get_loans(
    loan_status: Optional[LoanStatus] = Query(None, alias="status"),
    user_email: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
    db: Session = Depends(database_session),
    _current_user=Depends(get_current_active_user),
):
    return list_loans(db, loan_status, user_email, device_type)


@router.get("/details", response_model=list[LoanDetailResponse], summary="Consultar prestamos con detalles")
async def get_loan_details(
    loan_status: Optional[LoanStatus] = Query(None, alias="status"),
    user_email: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
    db: Session = Depends(database_session),
    _current_user=Depends(require_support),
):
    return [to_detail(loan) for loan in list_loans(db, loan_status, user_email, device_type)]


@router.get("/{loan_id}", response_model=LoanResponse, summary="Consultar prestamo")
async def get_loan_by_id(loan_id: int, db: Session = Depends(database_session)):
    loan = get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")
    return loan


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED, summary="Registrar prestamo")
@limiter.limit("10/minute")
async def create_new_loan(
    request: Request,
    data: LoanCreate,
    db: Session = Depends(database_session),
    _current_user=Depends(get_current_active_user),
):
    user = require_user(db, data.user_id)
    device = require_device(db, data.device_id)
    if not device.is_available:
        raise HTTPException(status_code=409, detail="El dispositivo no esta disponible")
    return create_loan(db, user, device)


@router.patch("/{loan_id}/return", response_model=LoanResponse, summary="Devolver dispositivo")
async def return_device(
    loan_id: int,
    db: Session = Depends(database_session),
    _current_user=Depends(require_support),
):
    loan = get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")
    if loan.status == "returned":
        raise HTTPException(status_code=409, detail="El prestamo ya fue devuelto")
    return return_loan(db, loan)
