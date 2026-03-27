from sqlalchemy import Column, Integer, String, DateTime, Boolean, Time, Date, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.schemas.enums import DoctorStatus


class Doctor(Base):
    __tablename__ = "doctors"

    id                           = Column(Integer, primary_key=True, index=True)
    name                         = Column(String(100), nullable=False)
    specialization               = Column(String(100), nullable=False)
    department                   = Column(String(100), nullable=False)
    branch                       = Column(String(100), nullable=False)
    phone                        = Column(String(15), unique=True, nullable=False)
    email                        = Column(String(100), unique=True, nullable=True)
    max_patients_per_day         = Column(Integer, default=20)
    consultation_duration_minutes = Column(Integer, default=15)
    status                       = Column(SAEnum(DoctorStatus), default=DoctorStatus.AVAILABLE)
    delay_minutes                = Column(Integer, default=0)
    is_active                    = Column(Boolean, default=True)
    created_at                   = Column(DateTime, default=datetime.utcnow)
    updated_at                   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    schedules       = relationship("DoctorSchedule", back_populates="doctor")
    leaves          = relationship("DoctorLeave", back_populates="doctor")
    appointments    = relationship("Appointment", back_populates="doctor")


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id           = Column(Integer, primary_key=True, index=True)
    doctor_id    = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    day_of_week  = Column(String(10), nullable=False)
    start_time   = Column(Time, nullable=False)
    end_time     = Column(Time, nullable=False)
    is_active    = Column(Boolean, default=True)
    valid_from   = Column(Date, nullable=False)
    valid_to     = Column(Date, nullable=True)

    doctor = relationship("Doctor", back_populates="schedules")


class DoctorLeave(Base):
    __tablename__ = "doctor_leaves"

    id          = Column(Integer, primary_key=True, index=True)
    doctor_id   = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    leave_date  = Column(Date, nullable=False)
    reason      = Column(String(255), nullable=True)
    is_full_day = Column(Boolean, default=True)
    start_time  = Column(Time, nullable=True)
    end_time    = Column(Time, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    doctor = relationship("Doctor", back_populates="leaves")
    appointments = relationship("Appointment", back_populates="doctor")