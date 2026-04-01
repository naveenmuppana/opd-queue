from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.schemas.slot import SlotGenerateRequest, SlotListResponse
from app.services import slot as slot_service

router = APIRouter(prefix="/slots", tags=["slots"])


@router.post("/generate", response_model=SlotListResponse, status_code=201)
def generate_slots(
    data: SlotGenerateRequest,
    db: Session = Depends(get_db)
):
    return slot_service.generate_slots(db, data)


@router.get("/", response_model=SlotListResponse)
def get_slots(
    doctor_id: int,
    slot_date: date = Query(...),
    db: Session = Depends(get_db)
):
    return slot_service.get_slots(db, doctor_id, slot_date)