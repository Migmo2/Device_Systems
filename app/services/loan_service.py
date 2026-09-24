"""Reglas de negocio y consultas relacionadas de prestamos."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User


def list_loans(
    db: Session,
    status: str | None = None,
    user_email: str | None = None,
    device_type: str | None = None,
) -> list[Loan]:
    query = select(Loan).options(joinedload(Loan.user), joinedload(Loan.device)).order_by(Loan.loan_date.desc())
    if status:
        query = query.where(Loan.status == status)
    if user_email:
        query = query.join(Loan.user).where(User.email == user_email.lower())
    if device_type:
        query = query.join(Loan.device).where(Device.device_type == device_type)
    return list(db.scalars(query).unique().all())


def get_loan(db: Session, loan_id: int) -> Loan | None:
    query = select(Loan).options(joinedload(Loan.user), joinedload(Loan.device)).where(Loan.id == loan_id)
    return db.scalar(query)


def create_loan(db: Session, user: User, device: Device) -> Loan:
    loan = Loan(user=user, device=device, status="active")
    device.is_available = False
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan: Loan) -> Loan:
    loan.status = "returned"
    loan.return_date = datetime.now(UTC)
    loan.device.is_available = True
    db.commit()
    db.refresh(loan)
    return loan


def to_detail(loan: Loan) -> dict:
    return {
        "loan_id": loan.id,
        "status": loan.status,
        "loan_date": loan.loan_date,
        "return_date": loan.return_date,
        "user": loan.user,
        "device": loan.device,
    }
