"""Modelo SQLAlchemy de dispositivos tecnologicos."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    loans = relationship("Loan", back_populates="device")
