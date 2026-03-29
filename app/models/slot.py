from sqlalchemy import Column, Integer, Date, Time, ForeignKey, Boolean
from sqlalchemy import Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.schemas.enums import SlotStatus


class Slot(Base):
    __tablename__ = "slots"

    id              = Column(Integer, primary_key=True, index=True)
    doctor_id       = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    slot_date       = Column(Date, nullable=False, index=True)
    slot_number     = Column(Integer, nullable=False)   # token = this
    start_time      = Column(Time, nullable=False)
    end_time        = Column(Time, nullable=False)
    status          = Column(SAEnum(SlotStatus), default=SlotStatus.AVAILABLE)
    is_emergency    = Column(Boolean, default=False)
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at      = Column(DateTime,
                             default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))

    doctor          = relationship("Doctor", backref="slots")
    appointment     = relationship("Appointment", back_populates="slot", uselist=False)

    __table_args__ = (
        # no two slots with same number for same doctor on same date
        __import__("sqlalchemy").UniqueConstraint(
            "doctor_id", "slot_date", "slot_number", name="uq_doctor_date_slot"
        ),
    )