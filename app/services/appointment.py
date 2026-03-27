from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date, time, timedelta
from typing import List, Optional
from app import models, schemas

class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_available_slots(self, doctor_id: int, appointment_date: date) -> List[schemas.TimeSlot]:
        """Get available time slots for a doctor on a specific date"""
        
        # Get doctor's schedule for that day of week
        day_of_week = appointment_date.strftime("%A").lower()
        schedule = self.db.query(models.DoctorSchedule).filter(
            and_(
                models.DoctorSchedule.doctor_id == doctor_id,
                models.DoctorSchedule.day_of_week == day_of_week,
                models.DoctorSchedule.is_active == True,
                models.DoctorSchedule.valid_from <= appointment_date,
                models.DoctorSchedule.valid_to >= appointment_date
            )
        ).first()
        
        if not schedule:
            return []
        
        # Check if doctor is on leave
        leave = self.db.query(models.DoctorLeave).filter(
            and_(
                models.DoctorLeave.doctor_id == doctor_id,
                models.DoctorLeave.leave_date == appointment_date
            )
        ).first()
        
        if leave:
            return []
        
        # Get doctor's consultation duration
        doctor = self.db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        slot_duration = doctor.consultation_duration_minutes
        
        # Generate all possible slots
        slots = []
        current_time = schedule.start_time
        end_time = schedule.end_time
        
        while current_time < end_time:
            slot_end = (datetime.combine(date.today(), current_time) + timedelta(minutes=slot_duration)).time()
            
            # Check if slot is already booked
            booked = self.db.query(models.Appointment).filter(
                and_(
                    models.Appointment.doctor_id == doctor_id,
                    models.Appointment.appointment_date >= datetime.combine(appointment_date, current_time),
                    models.Appointment.appointment_date < datetime.combine(appointment_date, slot_end),
                    models.Appointment.status.in_(["booked", "checked_in", "waiting", "called"])
                )
            ).first()
            
            slots.append(schemas.TimeSlot(
                start_time=current_time,
                end_time=slot_end,
                is_available=not booked,
                appointment_id=booked.id if booked else None
            ))
            
            current_time = slot_end
        
        return slots
    
    def create_appointment(self, appointment_data: schemas.AppointmentCreate) -> models.Appointment:
        """Create a new appointment with token generation"""
        
        # Check if slot is available
        appointment_date = appointment_data.appointment_date.date()
        slots = self.get_available_slots(appointment_data.doctor_id, appointment_date)
        
        slot_available = False
        for slot in slots:
            if slot.start_time == appointment_data.slot_start_time and slot.is_available:
                slot_available = True
                break
        
        if not slot_available:
            raise ValueError("Selected time slot is not available")
        
        # Generate token number
        max_token = self.db.query(func.max(models.Appointment.token_number)).filter(
            and_(
                models.Appointment.doctor_id == appointment_data.doctor_id,
                models.Appointment.appointment_date >= datetime.combine(appointment_date, time(0,0)),
                models.Appointment.appointment_date < datetime.combine(appointment_date + timedelta(days=1), time(0,0))
            )
        ).scalar() or 0
        
        token_number = max_token + 1
        
        # Create appointment
        db_appointment = models.Appointment(
            **appointment_data.model_dump(),
            token_number=token_number,
            queue_priority=schemas.QueuePriority.EMERGENCY if appointment_data.is_emergency else schemas.QueuePriority.NORMAL
        )
        
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        
        return db_appointment
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel appointment and promote waiting list if needed"""
        
        appointment = self.db.query(models.Appointment).filter(
            models.Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            return False
        
        if appointment.status in ["cancelled", "completed", "no_show"]:
            raise ValueError(f"Cannot cancel appointment with status: {appointment.status}")
        
        appointment.status = schemas.AppointmentStatus.CANCELLED
        self.db.commit()
        
        # Check waiting list and promote next patient
        waiting_entry = self.db.query(models.WaitingList).filter(
            and_(
                models.WaitingList.doctor_id == appointment.doctor_id,
                models.WaitingList.appointment_date == appointment.appointment_date.date(),
                models.WaitingList.status == "waiting"
            )
        ).order_by(models.WaitingList.position).first()
        
        if waiting_entry:
            waiting_entry.status = "promoted"
            self.db.commit()
        
        return True
    
    def get_queue_status(self, doctor_id: int, date: date) -> schemas.QueueStatusResponse:
        """Get current queue status for a doctor"""
        
        doctor = self.db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        
        # Get all active appointments for the day
        appointments = self.db.query(models.Appointment).filter(
            and_(
                models.Appointment.doctor_id == doctor_id,
                models.Appointment.appointment_date >= datetime.combine(date, time(0,0)),
                models.Appointment.appointment_date < datetime.combine(date + timedelta(days=1), time(0,0)),
                models.Appointment.status.in_(["booked", "checked_in", "waiting", "called", "in_consultation"])
            )
        ).order_by(models.Appointment.token_number).all()
        
        current_token = None
        waiting_count = 0
        queue = []
        
        for apt in appointments:
            if apt.status == "in_consultation":
                current_token = apt.token_number
            
            if apt.status in ["booked", "waiting", "called"]:
                waiting_count += 1
            
            queue.append(schemas.TokenResponse(
                token_number=apt.token_number,
                patient_name=apt.patient.name,
                doctor_name=doctor.name,
                queue_position=len(queue) + 1,
                estimated_wait_time=waiting_count * doctor.consultation_duration_minutes,
                status=apt.status
            ))
        
        return schemas.QueueStatusResponse(
            doctor_id=doctor_id,
            doctor_name=doctor.name,
            current_token=current_token,
            waiting_count=waiting_count,
            average_wait_time=doctor.consultation_duration_minutes,
            queue=queue
        )