from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, Time, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.schemas.enums import AppointmentStatus, QueuePriority, BookingType, WaitingListStatus


class Appointment(Base):
    __tablename__ = "appointments"

    id               = Column(Integer, primary_key=True, index=True)
    patient_id       = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id        = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    slot_id          = Column(Integer, ForeignKey("slots.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    slot_start_time  = Column(Time, nullable=False)
    slot_end_time    = Column(Time, nullable=False)
    token_number     = Column(Integer, nullable=False)
    queue_priority   = Column(SAEnum(QueuePriority), default=QueuePriority.NORMAL)
    status           = Column(SAEnum(AppointmentStatus), default=AppointmentStatus.BOOKED)
    booking_type     = Column(SAEnum(BookingType), default=BookingType.COUNTER)
    is_emergency     = Column(Boolean, default=False)
    created_at       = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at       = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    patient            = relationship("Patient", back_populates="appointments")
    doctor             = relationship("Doctor", back_populates="appointments")
    slot               = relationship("Slot", back_populates="appointment")
    waiting_list_entry = relationship("WaitingList", back_populates="appointment", uselist=False)


class WaitingList(Base):
    __tablename__ = "waiting_lists"

    id               = Column(Integer, primary_key=True, index=True)
    doctor_id        = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id       = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id   = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    appointment_date = Column(DateTime, nullable=False)
    position         = Column(Integer, nullable=False)
    status           = Column(SAEnum(WaitingListStatus), default=WaitingListStatus.WAITING)
    created_at       = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    doctor      = relationship("Doctor")
    patient     = relationship("Patient")
    appointment = relationship("Appointment", back_populates="waiting_list_entry")
    bb
    