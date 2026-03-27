from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app import schemas
from app.database import get_db
from app.services.appointment import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("/available-slots", response_model=List[schemas.TimeSlot])
def get_available_slots(
    doctor_id: int = Query(..., description="Doctor ID"),
    appointment_date: date = Query(..., description="Appointment date"),
    db: Session = Depends(get_db)
):
    """Get available time slots for a doctor on a specific date"""
    service = AppointmentService(db)
    return service.get_available_slots(doctor_id, appointment_date)

@router.post("/", response_model=schemas.AppointmentResponse, status_code=201)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    service = AppointmentService(db)
    try:
        return service.create_appointment(appointment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{appointment_id}", status_code=204)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    service = AppointmentService(db)
    try:
        if not service.cancel_appointment(appointment_id):
            raise HTTPException(status_code=404, detail="Appointment not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None

@router.get("/queue-status/{doctor_id}", response_model=schemas.QueueStatusResponse)
def get_queue_status(
    doctor_id: int,
    date: date = Query(..., description="Queue date"),
    db: Session = Depends(get_db)
):
    """Get current queue status for a doctor"""
    service = AppointmentService(db)
    return service.get_queue_status(doctor_id, date)g