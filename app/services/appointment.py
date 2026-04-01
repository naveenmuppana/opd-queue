from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime, timezone, date
from app.models.slot import Slot
from app.models.appointment import Appointment, WaitingList
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import (
    AppointmentCreate, AppointmentStatusUpdate, WaitingListResponse
)
from app.schemas.enums import AppointmentStatus, SlotStatus, WaitingListStatus, QueuePriority
from loguru import logger


def get_doctor_or_404(db: Session, doctor_id: int) -> Doctor:
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id, Doctor.is_active == True
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def get_patient_or_404(db: Session, patient_id: int) -> Patient:
    patient = db.query(Patient).filter(
        Patient.id == patient_id, Patient.is_active == True
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def get_slot_or_404(db: Session, slot_id: int) -> Slot:
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot


def get_next_waiting_position(db: Session, doctor_id: int, slot_date: date) -> int:
    last = db.query(func.max(WaitingList.position)).filter(
        WaitingList.doctor_id == doctor_id,
        func.date(WaitingList.appointment_date) == slot_date,
        WaitingList.status == WaitingListStatus.WAITING
    ).scalar()
    return (last or 0) + 1


def promote_from_waiting_list(db: Session, slot: Slot):
    """
    When a slot opens up, find the first waiting patient
    for that doctor on that date and book them into the slot.
    """
    next_waiting = db.query(WaitingList).filter(
        WaitingList.doctor_id == slot.doctor_id,
        func.date(WaitingList.appointment_date) == slot.slot_date,
        WaitingList.status == WaitingListStatus.WAITING
    ).order_by(WaitingList.position).first()

    if not next_waiting:
        return  # nobody waiting, slot stays available

    patient = get_patient_or_404(db, next_waiting.patient_id)

    # Create appointment for promoted patient
    appointment = Appointment(
        patient_id       = next_waiting.patient_id,
        doctor_id        = slot.doctor_id,
        slot_id          = slot.id,
        appointment_date = datetime.combine(slot.slot_date, slot.start_time),
        slot_start_time  = slot.start_time,
        slot_end_time    = slot.end_time,
        token_number     = slot.slot_number,
        status           = AppointmentStatus.BOOKED,
        booking_type     = next_waiting.appointment.booking_type
                           if next_waiting.appointment else "counter",
        queue_priority   = QueuePriority.NORMAL,
        is_emergency     = False
    )
    db.add(appointment)

    # Mark slot as booked
    slot.status = SlotStatus.BOOKED

    # Update waiting list entry
    next_waiting.status = WaitingListStatus.PROMOTED
    next_waiting.appointment = appointment

    db.commit()
    logger.info(
        f"Promoted patient {patient.patient_uid} "
        f"from waiting list into slot {slot.slot_number} "
        f"on {slot.slot_date}"
    )


def create_appointment(db: Session, data: AppointmentCreate) -> Appointment:
    doctor  = get_doctor_or_404(db, data.doctor_id)
    patient = get_patient_or_404(db, data.patient_id)
    slot    = get_slot_or_404(db, data.slot_id)

    # Validate slot belongs to this doctor
    if slot.doctor_id != data.doctor_id:
        raise HTTPException(
            status_code=400,
            detail="Slot does not belong to the specified doctor"
        )

    # If slot is taken → go to waiting list
    if slot.status != SlotStatus.AVAILABLE:
        position = get_next_waiting_position(db, data.doctor_id, slot.slot_date)
        waiting = WaitingList(
            doctor_id        = data.doctor_id,
            patient_id       = data.patient_id,
            appointment_date = datetime.combine(slot.slot_date, slot.start_time),
            position         = position,
            status           = WaitingListStatus.WAITING
        )
        db.add(waiting)
        db.commit()
        db.refresh(waiting)
        logger.info(
            f"Patient {patient.patient_uid} added to waiting list "
            f"position {position} for doctor {doctor.name} on {slot.slot_date}"
        )
        raise HTTPException(
            status_code=202,
            detail=f"Slot unavailable. Added to waiting list at position {position}"
        )

    # Book the slot
    appointment = Appointment(
        patient_id       = data.patient_id,
        doctor_id        = data.doctor_id,
        slot_id          = slot.id,
        appointment_date = datetime.combine(slot.slot_date, slot.start_time),
        slot_start_time  = slot.start_time,
        slot_end_time    = slot.end_time,
        token_number     = slot.slot_number,
        queue_priority   = data.queue_priority,
        status           = AppointmentStatus.BOOKED,
        booking_type     = data.booking_type,
        is_emergency     = data.is_emergency
    )

    slot.status = SlotStatus.BOOKED
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    logger.info(
        f"Appointment booked: token {slot.slot_number} | "
        f"patient {patient.patient_uid} | "
        f"doctor {doctor.name} | "
        f"slot {slot.start_time}–{slot.end_time}"
    )
    return appointment


def get_appointment_by_id(db: Session, appointment_id: int) -> Appointment:
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def get_appointments(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    doctor_id: int = None,
    patient_id: int = None,
    appointment_date: date = None,
    status: AppointmentStatus = None
) -> dict:
    query = db.query(Appointment)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if appointment_date:
        query = query.filter(func.date(Appointment.appointment_date) == appointment_date)
    if status:
        query = query.filter(Appointment.status == status)

    query = query.order_by(Appointment.token_number)
    total = query.count()
    appointments = query.offset((page - 1) * per_page).limit(per_page).all()

    return {"total": total, "page": page, "per_page": per_page, "appointments": appointments}


def update_appointment_status(
    db: Session, appointment_id: int, data: AppointmentStatusUpdate
) -> Appointment:
    appt = get_appointment_by_id(db, appointment_id)
    appt.status = data.status
    appt.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(appt)
    logger.info(f"Appointment {appointment_id} status → {data.status}")
    return appt


def cancel_appointment(db: Session, appointment_id: int) -> dict:
    appt = get_appointment_by_id(db, appointment_id)

    if appt.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel appointment with status '{appt.status}'"
        )

    appt.status = AppointmentStatus.CANCELLED
    appt.updated_at = datetime.now(timezone.utc)

    # Free up the slot
    slot = get_slot_or_404(db, appt.slot_id)
    slot.status = SlotStatus.AVAILABLE
    db.commit()

    # Auto-promote first waiting patient
    promote_from_waiting_list(db, slot)

    logger.info(f"Appointment {appointment_id} cancelled, slot {slot.slot_number} freed")
    return {"message": f"Appointment {appointment_id} cancelled successfully"}


def get_queue(db: Session, doctor_id: int, appointment_date: date) -> list:
    return db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        func.date(Appointment.appointment_date) == appointment_date,
        Appointment.status.notin_([
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.NO_SHOW
        ])
    ).order_by(Appointment.token_number).all()


def get_waiting_list(db: Session, doctor_id: int, appointment_date: date) -> list:
    return db.query(WaitingList).filter(
        WaitingList.doctor_id == doctor_id,
        func.date(WaitingList.appointment_date) == appointment_date,
        WaitingList.status == WaitingListStatus.WAITING
    ).order_by(WaitingList.position).all()