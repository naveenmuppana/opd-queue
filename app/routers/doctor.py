from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas
from app.database import get_db
from app.services.doctor import DoctorService

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.post("/", response_model=schemas.DoctorResponse, status_code=201)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    service = DoctorService(db)
    try:
        return service.create(doctor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.DoctorResponse])
def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    specialization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = DoctorService(db)
    return service.list(skip, limit, specialization)

@router.get("/{doctor_id}", response_model=schemas.DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    service = DoctorService(db)
    doctor = service.get(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.get("/email/{email}", response_model=schemas.DoctorResponse)
def get_doctor_by_email(email: str, db: Session = Depends(get_db)):
    service = DoctorService(db)
    doctor = service.get_by_email(email)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.put("/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor: schemas.DoctorUpdate,
    db: Session = Depends(get_db)
):
    service = DoctorService(db)
    updated = service.update(doctor_id, doctor)
    if not updated:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated

@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    service = DoctorService(db)
    if not service.delete(doctor_id):
        raise HTTPException(status_code=404, detail="Doctor not found")
    return None