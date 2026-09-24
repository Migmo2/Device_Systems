"""Endpoints CRUD y filtros del recurso devices."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import database_session
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceResponse, DeviceType, DeviceUpdate
from app.services.device_service import (
    create_device,
    delete_device,
    get_device,
    list_devices,
    serial_exists,
    update_device,
)

router = APIRouter(prefix="/devices", tags=["Devices"])


def require_device(db: Session, device_id: int):
    device = get_device(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device


@router.get("", response_model=list[DeviceResponse], summary="Listar dispositivos")
async def get_devices(
    device_type: Optional[DeviceType] = Query(None),
    is_available: Optional[bool] = Query(None),
    brand: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(database_session),
):
    return list_devices(db, device_type, is_available, brand, search)


@router.get("/{device_id}", response_model=DeviceResponse, summary="Consultar dispositivo")
async def get_device_by_id(device_id: int, db: Session = Depends(database_session)):
    return require_device(db, device_id)


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, summary="Crear dispositivo")
async def create_new_device(data: DeviceCreate, db: Session = Depends(database_session)):
    payload = data.model_dump()
    if serial_exists(db, payload["serial_number"]):
        raise HTTPException(status_code=400, detail="El numero de serie ya esta registrado")
    try:
        return create_device(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El numero de serie ya esta registrado") from None


@router.put("/{device_id}", response_model=DeviceResponse, summary="Actualizar dispositivo")
async def replace_device(device_id: int, data: DeviceUpdate, db: Session = Depends(database_session)):
    device = require_device(db, device_id)
    payload = data.model_dump()
    if serial_exists(db, payload["serial_number"], device_id):
        raise HTTPException(status_code=400, detail="El numero de serie ya esta registrado")
    return update_device(db, device, payload)


@router.patch("/{device_id}", response_model=DeviceResponse, summary="Actualizar dispositivo parcialmente")
async def patch_device(device_id: int, data: DevicePatch, db: Session = Depends(database_session)):
    device = require_device(db, device_id)
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo")
    if "serial_number" in payload and serial_exists(db, payload["serial_number"], device_id):
        raise HTTPException(status_code=400, detail="El numero de serie ya esta registrado")
    return update_device(db, device, payload)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar dispositivo")
async def remove_device(device_id: int, db: Session = Depends(database_session)):
    device = require_device(db, device_id)
    if device.loans:
        raise HTTPException(status_code=409, detail="No se puede eliminar un dispositivo con historial")
    delete_device(db, device)
