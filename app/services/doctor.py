from sqlalchemy.orm import Session
from app import models, schemas
from datetime import date

class DoctorService:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, doctor_data: schemas.DoctorCreate):
        # Check if doctor with same email exists
        existing = self.db.query(models.Doctor).filter(
            models.Doctor.email == doctor_data.email
        ).first()
        if existing:
            raise ValueError("Doctor with this email already exists")
        
        # Create doctor
        db_doctor = models.Doctor(**doctor_data.model_dump())
        self.db.add(db_doctor)
        self.db.flush()  # Get ID for any derived fields if needed
        self.db.commit()
        self.db.refresh(db_doctor)
        return db_doctor
    
    def get(self, doctor_id: int):
        return self.db.query(models.Doctor).filter(
            models.Doctor.id == doctor_id,
            models.Doctor.is_active == True
        ).first()
    
    def get_by_email(self, email: str):
        return self.db.query(models.Doctor).filter(
            models.Doctor.email == email
        ).first()
    
    def list(self, skip: int = 0, limit: int = 100, specialty: str = None):
        query = self.db.query(models.Doctor).filter(models.Doctor.is_active == True)
        if specialty:
            query = query.filter(models.Doctor.specialty == specialty)
        return query.offset(skip).limit(limit).all()
    
    def update(self, doctor_id: int, doctor_data: schemas.DoctorUpdate):
        db_doctor = self.get(doctor_id)
        if not db_doctor:
            return None
        
        update_data = doctor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_doctor, field, value)
        
        self.db.commit()
        self.db.refresh(db_doctor)
        return db_doctor
    
    def delete(self, doctor_id: int):
        db_doctor = self.get(doctor_id)
        if db_doctor:
            db_doctor.is_active = False
            self.db.commit()
            return True
        return False