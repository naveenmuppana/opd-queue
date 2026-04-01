from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime
from app.models.patient import Patient, EmergencyContact
from app.schemas.patient import PatientCreate, PatientUpdate
from loguru import logger


def generate_patient_uid(patient_id: int) -> str:
    year = datetime.now().year
    return f"MED-{year}-{patient_id:05d}"


def check_existing_patient(db: Session, phone: str) -> Patient | None:
    return db.query(Patient).filter(
        Patient.phone == phone,
        Patient.is_active == True
    ).first()


def get_patient_by_id(db: Session, patient_id: int) -> Patient:
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.is_active == True
    ).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found"
        )
    return patient


def get_patients(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: str = None,
) -> dict:
    query = db.query(Patient).filter(Patient.is_active == True)

    if search:
        query = query.filter(
            Patient.name.ilike(f"%{search}%") |
            Patient.phone.ilike(f"%{search}%") |
            Patient.patient_uid.ilike(f"%{search}%")
        )

    total = query.count()
    patients = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "patients": patients
    }


def create_patient(db: Session, data: PatientCreate) -> Patient:
    existing = check_existing_patient(db, data.phone)
    if existing:
        logger.info(f"Existing patient found for phone {data.phone}")
        return existing

    try:
        emergency_contacts = data.emergency_contacts or []
        patient_data = data.model_dump(exclude={"emergency_contacts"})

        patient = Patient(**patient_data)
        db.add(patient)
        db.flush()

        patient.patient_uid = generate_patient_uid(patient.id)

        for contact_data in emergency_contacts:
            contact = EmergencyContact(
                patient_id=patient.id,
                **contact_data.model_dump()
            )
            db.add(contact)

        db.commit()
        db.refresh(patient)
        logger.info(f"New patient created: {patient.patient_uid}")
        return patient

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this phone, email or aadhaar already exists"
        )


def update_patient(
    db: Session,
    patient_id: int,
    data: PatientUpdate
) -> Patient:
    patient = get_patient_by_id(db, patient_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    logger.info(f"Patient {patient.patient_uid} updated")
    return patient


def deactivate_patient(db: Session, patient_id: int) -> dict:
    patient = get_patient_by_id(db, patient_id)
    patient.is_active = False
    patient.updated_at = datetime.utcnow()
    db.commit()
    logger.info(f"Patient {patient.patient_uid} deactivated")
    return {"message": f"Patient {patient.patient_uid} deactivated"}