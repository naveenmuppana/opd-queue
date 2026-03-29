from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.schemas.enums import PatientType


class EmergencyContactCreate(BaseModel):
    name: str
    relation_type: str
    phone: str
    is_primary: bool = False

    @field_validator("phone")
    @classmethod
    def phone_must_be_valid(cls, v):
        v = v.strip()
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone must be 10 digits")
        return v


class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    relation_type: str
    phone: str
    is_primary: bool

    model_config = {"from_attributes": True}


class PatientCreate(BaseModel):
    name: str
    phone: str
    gender: str
    age: int
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    blood_group: Optional[str] = None
    aadhaar_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    insurance_company: Optional[str] = None
    policy_number: Optional[str] = None
    tpa_name: Optional[str] = None
    tpa_id: Optional[str] = None
    insurance_valid_from: Optional[date] = None
    insurance_valid_to: Optional[date] = None
    coverage_amount: Optional[Decimal] = None
    emergency_contacts: Optional[list[EmergencyContactCreate]] = []

    @field_validator("phone")
    @classmethod
    def phone_must_be_valid(cls, v):
        v = v.strip()
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone must be 10 digits")
        return v

    @field_validator("age")
    @classmethod
    def age_must_be_valid(cls, v):
        if v < 0 or v > 120:
            raise ValueError("Age must be between 0 and 120")
        return v

    @field_validator("gender")
    @classmethod
    def gender_must_be_valid(cls, v):
        v = v.strip().lower()
        if v not in ("male", "female", "other"):
            raise ValueError("Gender must be male, female or other")
        return v

    @field_validator("blood_group")
    @classmethod
    def blood_group_must_be_valid(cls, v):
        if v is None:
            return v
        valid = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        if v.upper() not in valid:
            raise ValueError("Invalid blood group")
        return v.upper()

    @field_validator("aadhaar_number")
    @classmethod
    def aadhaar_must_be_valid(cls, v):
        if v is None:
            return v
        if not v.isdigit() or len(v) != 12:
            raise ValueError("Aadhaar must be 12 digits")
        return v


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    insurance_company: Optional[str] = None
    policy_number: Optional[str] = None
    tpa_name: Optional[str] = None
    tpa_id: Optional[str] = None
    insurance_valid_from: Optional[date] = None
    insurance_valid_to: Optional[date] = None
    coverage_amount: Optional[Decimal] = None


class PatientResponse(BaseModel):
    id: int
    patient_uid: Optional[str] = None
    name: str
    phone: str
    email: Optional[str] = None
    age: int
    gender: str
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    aadhaar_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    insurance_company: Optional[str] = None
    policy_number: Optional[str] = None
    coverage_amount: Optional[Decimal] = None
    insurance_valid_from: Optional[date] = None
    insurance_valid_to: Optional[date] = None
    patient_type: PatientType
    is_active: bool
    created_at: datetime
    emergency_contacts: list[EmergencyContactResponse] = []

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    patients: list[PatientResponse]