from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date, time
from app.schemas.enums import AppointmentStatus, QueuePriority

# Appointment Schemas
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    slot_start_time: time
    slot_end_time: time
    booking_type: str = "counter"
    is_emergency: bool = False

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    queue_priority: Optional[QueuePriority] = None
    token_number: Optional[int] = None

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    slot_start_time: time
    slot_end_time: time
    token_number: int
    queue_priority: QueuePriority
    status: AppointmentStatus
    booking_type: str
    is_emergency: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Waiting List Schemas
class WaitingListBase(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: date
    preferred_time: Optional[time] = None

class WaitingListCreate(WaitingListBase):
    pass

class WaitingListResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: date
    preferred_time: Optional[time] = None
    status: str
    position: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Slot Schemas
class TimeSlot(BaseModel):
    start_time: time
    end_time: time
    is_available: bool = True
    appointment_id: Optional[int] = None

class DoctorAvailabilityRequest(BaseModel):
    doctor_id: int
    date: date

class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    date: date
    available_slots: list[TimeSlot]
    total_slots: int
    booked_slots: int

# Queue Management Schemas
class TokenResponse(BaseModel):
    token_number: int
    patient_name: str
    doctor_name: str
    queue_position: int
    estimated_wait_time: int  # in minutes
    status: AppointmentStatus

class QueueStatusResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    current_token: Optional[int]
    waiting_count: int
    average_wait_time: int
    queue: list[TokenResponse]