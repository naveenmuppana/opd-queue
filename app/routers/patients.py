from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)
from app.services import patient as patient_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "/register",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def register_patient(
    data: PatientCreate,
    db: Session = Depends(get_db)
):
    return patient_service.create_patient(db, data)


@router.get(
    "/",
    response_model=PatientListResponse
)
def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Records per page"),
    search: str = Query(None, description="Search by name, phone or patient UID"),
    db: Session = Depends(get_db)
):
    return patient_service.get_patients(db, page, per_page, search)


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    return patient_service.get_patient_by_id(db, patient_id)


@router.get(
    "/phone/{phone}",
    response_model=PatientResponse
)
def get_patient_by_phone(
    phone: str,
    db: Session = Depends(get_db)
):
    patient = patient_service.check_existing_patient(db, phone)
    if not patient:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No patient found with phone {phone}"
        )
    return patient


@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Session = Depends(get_db)
):
    return patient_service.update_patient(db, patient_id, data)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_200_OK
)
def deactivate_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    return patient_service.deactivate_patient(db, patient_id)