from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import date, time, datetime
from app.schemas.enums import DoctorStatus


class DoctorScheduleCreate(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time
    valid_from: date
    valid_to: Optional[date] = None

    @field_validator("day_of_week")
    @classmethod
    def day_must_be_valid(cls, v):
        valid = {"monday", "tuesday", "wednesday",
                 "thursday", "friday", "saturday", "sunday"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid day: {v}")
        return v.lower()

    @field_validator("end_time")
    @classmethod
    def end_must_be_after_start(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class DoctorScheduleResponse(BaseModel):
    id: int
    day_of_week: str
    start_time: time
    end_time: time
    valid_from: date
    valid_to: Optional[date] = None
    is_active: bool

    model_config = {"from_attributes": True}


class DoctorLeaveCreate(BaseModel):
    leave_date: date
    reason: Optional[str] = None
    is_full_day: bool = True
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @field_validator("leave_date")
    @classmethod
    def leave_date_must_be_future(cls, v):
        if v < date.today():
            raise ValueError("Leave date cannot be in the past")
        return v


class DoctorLeaveResponse(BaseModel):
    id: int
    leave_date: date
    reason: Optional[str] = None
    is_full_day: bool
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DoctorCreate(BaseModel):
    name: str
    specialization: str
    department: str
    branch: str
    phone: str
    email: Optional[EmailStr] = None
    max_patients_per_day: int = 20
    consultation_duration_minutes: int = 15
    schedules: Optional[list[DoctorScheduleCreate]] = []

    @field_validator("phone")
    @classmethod
    def phone_must_be_valid(cls, v):
        v = v.strip()
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone must be 10 digits")
        return v

    @field_validator("max_patients_per_day")
    @classmethod
    def max_patients_must_be_valid(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Max patients must be between 1 and 100")
        return v

    @field_validator("consultation_duration_minutes")
    @classmethod
    def duration_must_be_valid(cls, v):
        if v < 5 or v > 60:
            raise ValueError("Duration must be between 5 and 60 minutes")
        return v


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    department: Optional[str] = None
    branch: Optional[str] = None
    email: Optional[EmailStr] = None
    max_patients_per_day: Optional[int] = None
    consultation_duration_minutes: Optional[int] = None
    status: Optional[DoctorStatus] = None
    delay_minutes: Optional[int] = None


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    department: str
    branch: str
    phone: str
    email: Optional[str] = None
    max_patients_per_day: int
    consultation_duration_minutes: int
    status: DoctorStatus
    delay_minutes: int
    is_active: bool
    created_at: datetime
    schedules: list[DoctorScheduleResponse] = []

    model_config = {"from_attributes": True}


class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    department: str
    date: date
    is_available: bool
    reason: Optional[str] = None
    available_slots: int
    next_available_slot: Optional[time] = None