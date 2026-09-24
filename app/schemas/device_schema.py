"""Schemas Pydantic para dispositivos."""

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


DeviceType = Literal["laptop", "tablet", "proyector", "camara", "router", "monitor"]


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    serial_number: str = Field(..., min_length=3, max_length=80)
    device_type: DeviceType
    brand: str | None = Field(default=None, max_length=80)
    is_available: bool = True


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass


class DevicePatch(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    serial_number: str | None = Field(default=None, min_length=3, max_length=80)
    device_type: DeviceType | None = None
    brand: str | None = Field(default=None, max_length=80)
    is_available: bool | None = None


class DeviceResponse(DeviceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
