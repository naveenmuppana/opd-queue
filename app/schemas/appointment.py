from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import date, time, datetime
from app.schemas.enums import (
    AppointmentStatus, QueuePriority, BookingType, ConsultationType
)


class AppointmentCreate(BaseModel):
    patient_id:       int
    doctor_id:        int
    slot_id:          int
    consultation_type: ConsultationType
    queue_priority:   QueuePriority = QueuePriority.NORMAL
    booking_type:     BookingType = BookingType.COUNTER
    is_emergency:     bool = False


class AppointmentResponse(BaseModel):
    id:               int
    patient_id:       int
    doctor_id:        int
    slot_id:          int
    appointment_date: datetime
    slot_start_time:  time
    slot_end_time:    time
    token_number:     int
    queue_priority:   QueuePriority
    status:           AppointmentStatus
    booking_type:     BookingType
    is_emergency:     bool
    created_at:       datetime

    model_config = {"from_attributes": True}


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentListResponse(BaseModel):
    total:        int
    page:         int
    per_page:     int
    appointments: list[AppointmentResponse]


class WaitingListResponse(BaseModel):
    id:               int
    doctor_id:        int
    patient_id:       int
    appointment_date: datetime
    position:         int
    status:           str

    model_config = {"from_attributes": True}
