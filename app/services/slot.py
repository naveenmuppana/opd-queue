from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone, date
from app.models.slot import Slot
from app.models.doctor import Doctor, DoctorSchedule, DoctorLeave
from app.schemas.enums import SlotStatus
from app.schemas.slot import SlotGenerateRequest, SlotListResponse, SlotResponse
from loguru import logger


def get_doctor_schedule_for_date(
    db: Session, doctor_id: int, slot_date: date
) -> DoctorSchedule:
    day_name = slot_date.strftime("%A").lower()
    schedule = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.day_of_week == day_name,
        DoctorSchedule.is_active == True,
        DoctorSchedule.valid_from <= slot_date,
        (DoctorSchedule.valid_to == None) | (DoctorSchedule.valid_to >= slot_date)
    ).first()
    if not schedule:
        raise HTTPException(
            status_code=400,
            detail=f"Doctor has no schedule on {day_name.capitalize()}"
        )
    return schedule


def generate_slots(db: Session, data: SlotGenerateRequest) -> SlotListResponse:
    # Validate doctor exists
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id,
        Doctor.is_active == True
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check not on leave
    on_leave = db.query(DoctorLeave).filter(
        DoctorLeave.doctor_id == data.doctor_id,
        DoctorLeave.leave_date == data.slot_date,
        DoctorLeave.is_full_day == True
    ).first()
    if on_leave:
        raise HTTPException(
            status_code=400,
            detail="Doctor is on leave on this date — cannot generate slots"
        )

    # Check slots not already generated
    existing = db.query(func.count(Slot.id)).filter(
        Slot.doctor_id == data.doctor_id,
        Slot.slot_date == data.slot_date
    ).scalar()
    if existing > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Slots already generated for this doctor on {data.slot_date}"
        )

    schedule = get_doctor_schedule_for_date(db, data.doctor_id, data.slot_date)

    # Generate equal-interval slots within working hours
    base = datetime.combine(data.slot_date, schedule.start_time)
    end  = datetime.combine(data.slot_date, schedule.end_time)
    duration = doctor.consultation_duration_minutes
    slot_number = 1
    slots_created = []

    while base + timedelta(minutes=duration) <= end and slot_number <= doctor.max_patients_per_day:
        slot_end = base + timedelta(minutes=duration)
        slot = Slot(
            doctor_id   = data.doctor_id,
            slot_date   = data.slot_date,
            slot_number = slot_number,
            start_time  = base.time(),
            end_time    = slot_end.time(),
            status      = SlotStatus.AVAILABLE
        )
        db.add(slot)
        slots_created.append(slot)
        base = slot_end
        slot_number += 1

    db.commit()
    for s in slots_created:
        db.refresh(s)

    logger.info(
        f"Generated {len(slots_created)} slots for "
        f"doctor {doctor.name} on {data.slot_date}"
    )

    return SlotListResponse(
        doctor_id       = data.doctor_id,
        slot_date       = data.slot_date,
        total_slots     = len(slots_created),
        available_slots = len(slots_created),
        booked_slots    = 0,
        slots           = [SlotResponse.model_validate(s) for s in slots_created]
    )


def get_slots(db: Session, doctor_id: int, slot_date: date) -> SlotListResponse:
    slots = db.query(Slot).filter(
        Slot.doctor_id == doctor_id,
        Slot.slot_date == slot_date
    ).order_by(Slot.slot_number).all()

    if not slots:
        raise HTTPException(
            status_code=404,
            detail="No slots found. Please generate slots for this date first."
        )

    available = sum(1 for s in slots if s.status == SlotStatus.AVAILABLE)

    return SlotListResponse(
        doctor_id       = doctor_id,
        slot_date       = slot_date,
        total_slots     = len(slots),
        available_slots = available,
        booked_slots    = len(slots) - available,
        slots           = [SlotResponse.model_validate(s) for s in slots]
    )