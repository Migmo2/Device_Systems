"""Logica CRUD y filtros de dispositivos."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.device_model import Device


def list_devices(
    db: Session,
    device_type: str | None = None,
    is_available: bool | None = None,
    brand: str | None = None,
    search: str | None = None,
) -> list[Device]:
    query = select(Device).order_by(Device.name)
    if device_type:
        query = query.where(Device.device_type == device_type)
    if is_available is not None:
        query = query.where(Device.is_available == is_available)
    if brand:
        query = query.where(Device.brand.ilike(f"%{brand}%"))
    if search:
        term = f"%{search}%"
        query = query.where(or_(Device.name.ilike(term), Device.serial_number.ilike(term)))
    return list(db.scalars(query).all())


def create_device(db: Session, data: dict) -> Device:
    device = Device(**data)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_device(db: Session, device_id: int) -> Device | None:
    return db.get(Device, device_id)


def update_device(db: Session, device: Device, data: dict) -> Device:
    for field, value in data.items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device: Device) -> None:
    db.delete(device)
    db.commit()


def serial_exists(db: Session, serial_number: str, exclude_id: int | None = None) -> bool:
    query = select(Device).where(Device.serial_number == serial_number)
    if exclude_id is not None:
        query = query.where(Device.id != exclude_id)
    return db.scalar(query) is not None
