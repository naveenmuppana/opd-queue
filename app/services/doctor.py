from sqlalchemy.orm import Session
from app import models, schemas


class DoctorService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, doctor_data: schemas.DoctorCreate):
        existing = self.db.query(models.Doctor).filter(
            models.Doctor.email == doctor_data.email
        ).first()
        if existing:
            raise ValueError("Doctor with this email already exists")

        schedules_data = doctor_data.schedules or []
        doctor_dict = doctor_data.model_dump(exclude={"schedules"})

        db_doctor = models.Doctor(**doctor_dict)
        self.db.add(db_doctor)
        self.db.flush()

        for schedule in schedules_data:
            db_schedule = models.DoctorSchedule(
                doctor_id=db_doctor.id,
                **schedule.model_dump()
            )
            self.db.add(db_schedule)

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

    def list(self, skip: int = 0, limit: int = 100, specialization: str = None):
        query = self.db.query(models.Doctor).filter(models.Doctor.is_active == True)
        if specialization:
            query = query.filter(models.Doctor.specialization == specialization)
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