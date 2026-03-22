from enum import Enum


class PatientType(str, Enum):
    NEW = "new"
    EXISTING = "existing"


class ConsultationType(str, Enum):
    NORMAL = "normal"
    EMR = "emr"
    EMERGENCY = "emergency"


class BookingType(str, Enum):
    ONLINE = "online"
    COUNTER = "counter"


class AppointmentStatus(str, Enum):
    BOOKED = "booked"
    CHECKED_IN = "checked_in"
    LATE = "late"
    WAITING = "waiting"
    CALLED = "called"
    IN_CONSULTATION = "in_consultation"
    INVESTIGATION_PENDING = "investigation_pending"
    COMPLETED = "completed"
    FOLLOWUP_SCHEDULED = "followup_scheduled"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class QueuePriority(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class DoctorStatus(str, Enum):
    AVAILABLE = "available"
    IN_CONSULTATION = "in_consultation"
    ON_LEAVE = "on_leave"
    DELAYED = "delayed"
    PAUSED = "paused"
    UNAVAILABLE = "unavailable"


class SlotStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WaitingListStatus(str, Enum):
    WAITING = "waiting"
    PROMOTED = "promoted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class InvestigationType(str, Enum):
    BLOOD_TEST = "blood_test"
    XRAY = "xray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    ULTRASOUND = "ultrasound"
    ECG = "ecg"
    OTHER = "other"


class InvestigationStatus(str, Enum):
    PRESCRIBED = "prescribed"
    SAMPLE_COLLECTED = "sample_collected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"