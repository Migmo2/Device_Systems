"""Schemas Pydantic para prestamos y consultas relacionadas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


LoanStatus = Literal["active", "returned", "overdue"]


class LoanCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    device_id: int = Field(..., gt=0)


class LoanUpdate(BaseModel):
    status: LoanStatus


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: datetime | None
    status: LoanStatus
    model_config = ConfigDict(from_attributes=True)


class RelatedUser(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class RelatedDevice(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(BaseModel):
    loan_id: int
    status: LoanStatus
    loan_date: datetime
    return_date: datetime | None
    user: RelatedUser
    device: RelatedDevice
