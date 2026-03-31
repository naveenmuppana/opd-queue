from app.schemas.enums import *
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
    EmergencyContactCreate,
    EmergencyContactResponse,
)
from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorScheduleCreate,
    DoctorScheduleResponse,
    DoctorLeaveCreate,
    DoctorLeaveResponse,
    DoctorAvailabilityResponse,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
    AppointmentListResponse,
    WaitingListResponse,
)
from app.schemas.slot import (
    SlotGenerateRequest,
    SlotResponse,
    SlotListResponse,
)
