from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Boolean, Date, Numeric, Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.schemas.enums import PatientType


class Patient(Base):
    __tablename__ = "patients"

    id                  = Column(Integer, primary_key=True, index=True)
    patient_uid         = Column(String(20), unique=True, index=True)
    name                = Column(String(100), nullable=False)
    phone               = Column(String(15), unique=True, nullable=False, index=True)
    email               = Column(String(100), unique=True, nullable=True)
    age                 = Column(Integer, nullable=False)
    gender              = Column(String(10), nullable=False)
    blood_group         = Column(String(5), nullable=True)
    date_of_birth       = Column(Date, nullable=True)

    aadhaar_number      = Column(String(12), unique=True, nullable=True)
    address             = Column(String(255), nullable=True)
    city                = Column(String(100), nullable=True)
    state               = Column(String(100), nullable=True)
    pincode             = Column(String(10), nullable=True)

    insurance_company   = Column(String(100), nullable=True)
    policy_number       = Column(String(50), unique=True, nullable=True)
    tpa_name            = Column(String(100), nullable=True)
    tpa_id              = Column(String(50), nullable=True)
    insurance_valid_from = Column(Date, nullable=True)
    insurance_valid_to  = Column(Date, nullable=True)
    coverage_amount     = Column(Numeric(10, 2), nullable=True)

    patient_type        = Column(SAEnum(PatientType), default=PatientType.NEW)
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow,
                                 onupdate=datetime.utcnow)

    emergency_contacts  = relationship("EmergencyContact",
                                       back_populates="patient")
    medical_histories   = relationship("MedicalHistory",
                                       back_populates="patient")
    appointments        = relationship("Appointment",
                                       back_populates="patient")


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id           = Column(Integer, primary_key=True, index=True)
    patient_id   = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name         = Column(String(100), nullable=False)
    relationship = Column(String(50), nullable=False)
    phone        = Column(String(15), nullable=False)
    is_primary   = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="emergency_contacts")


class MedicalHistory(Base):
    __tablename__ = "medical_histories"

    id              = Column(Integer, primary_key=True, index=True)
    patient_id      = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id       = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    condition       = Column(String(200), nullable=False)
    diagnosed_date  = Column(Date, nullable=True)
    is_current      = Column(Boolean, default=True)
    notes           = Column(String(500), nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="medical_histories")