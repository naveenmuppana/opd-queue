from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from app.schemas.enums import SlotStatus


class SlotGenerateRequest(BaseModel):
    doctor_id: int
    slot_date: date


class SlotResponse(BaseModel):
    id: int
    doctor_id: int
    slot_date: date
    slot_number: int
    start_time: time
    end_time: time
    status: SlotStatus
    is_emergency: bool

    model_config = {"from_attributes": True}


class SlotListResponse(BaseModel):
    doctor_id: int
    slot_date: date
    total_slots: int
    available_slots: int
    booked_slots: int
    slots: list[SlotResponse]
