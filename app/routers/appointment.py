from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.database import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
    AppointmentListResponse,
    WaitingListResponse
)
from app.schemas.enums import AppointmentStatus
from app.services import appointment as appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    return appointment_service.create_appointment(db, data)


@router.get("/queue", response_model=list[AppointmentResponse])
def get_queue(
    doctor_id: int,
    appointment_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    target_date = appointment_date or date.today()
    return appointment_service.get_queue(db, doctor_id, target_date)


@router.get("/waiting-list", response_model=list[WaitingListResponse])
def get_waiting_list(
    doctor_id: int,
    appointment_date: date,
    db: Session = Depends(get_db)
):
    return appointment_service.get_waiting_list(db, doctor_id, appointment_date)


@router.get("/", response_model=AppointmentListResponse)
def list_appointments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    appointment_date: Optional[date] = None,
    status: Optional[AppointmentStatus] = None,
    db: Session = Depends(get_db)
):
    return appointment_service.get_appointments(
        db, page, per_page, doctor_id, patient_id, appointment_date, status
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    return appointment_service.get_appointment_by_id(db, appointment_id)


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    db: Session = Depends(get_db)
):
    return appointment_service.update_appointment_status(db, appointment_id, data)


@router.delete("/{appointment_id}", status_code=status.HTTP_200_OK)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    return appointment_service.cancel_appointment(db, appointment_id)
