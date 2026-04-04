# OPD Queue Management System

A production-ready **Hospital Outpatient Department (OPD) Queue Management API** built with Python and FastAPI. The system manages end-to-end patient flow — from registration and doctor scheduling to slot-based appointment booking and live queue management.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Logging | Loguru |
| Server | Uvicorn |

---

## Project Structure

```
opd-queue/
├── app/
│   ├── main.py              # FastAPI app, middleware, router registration
│   ├── config.py            # Environment-based settings (pydantic-settings)
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── patient.py       # Patient, EmergencyContact, MedicalHistory
│   │   ├── doctor.py        # Doctor, DoctorSchedule, DoctorLeave
│   │   ├── slot.py          # Slot (pre-generated time slots)
│   │   └── appointment.py   # Appointment, WaitingList
│   ├── schemas/
│   │   ├── enums.py         # All enums (AppointmentStatus, SlotStatus, etc.)
│   │   ├── patient.py       # Patient Pydantic schemas
│   │   ├── doctor.py        # Doctor Pydantic schemas
│   │   ├── slot.py          # Slot schemas
│   │   └── appointment.py   # Appointment schemas
│   ├── routers/
│   │   ├── patients.py      # Patient endpoints
│   │   ├── doctor.py        # Doctor endpoints
│   │   ├── slot.py          # Slot generation endpoints
│   │   └── appointment.py   # Appointment + queue endpoints
│   └── services/
│       ├── patient.py       # Patient business logic
│       ├── doctor.py        # Doctor business logic
│       ├── slot.py          # Slot generation logic
│       └── appointment.py   # Booking, cancellation, queue logic
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── .env                     # Environment variables (not committed)
├── alembic.ini
└── requirements.txt
```

---

## Setup & Installation

### Prerequisites
- Python 3.12+
- PostgreSQL
- Git

### Steps

```bash
# Clone the repo
git clone https://github.com/naveenmuppana/opd-queue.git
cd opd-queue

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Environment Variables (.env)

```
database_url=postgresql://user:password@localhost:5432/opd_queue
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REDIS_URL=redis://localhost:6379
DEBUG=False
GRACE_PERIOD_MINUTES=15
SLOT_RESERVATION_MINUTES=10
MAX_PATIENTS_PER_DAY=20
```

---

## API Overview

Once running, visit **http://127.0.0.1:8000/docs** for the full interactive Swagger UI.

### Patients — `/patients`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/patients/register` | Register a new patient |
| GET | `/patients/` | List patients (paginated, searchable) |
| GET | `/patients/{id}` | Get patient by ID |
| GET | `/patients/phone/{phone}` | Get patient by phone |
| PUT | `/patients/{id}` | Update patient details |
| DELETE | `/patients/{id}` | Soft deactivate patient |

### Doctors — `/doctors`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/doctors/` | Create doctor with schedules |
| GET | `/doctors/` | List doctors (filter by specialization) |
| GET | `/doctors/{id}` | Get doctor by ID |
| PUT | `/doctors/{id}` | Update doctor details |
| DELETE | `/doctors/{id}` | Soft deactivate doctor |

### Slots — `/slots`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/slots/generate` | Generate slots for a doctor on a date |
| GET | `/slots/` | View all slots with availability |

### Appointments — `/appointments`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/appointments/` | Book an appointment |
| GET | `/appointments/` | List appointments (filter by doctor/patient/date/status) |
| GET | `/appointments/queue` | Live queue for a doctor on a date |
| GET | `/appointments/waiting-list` | Waiting list for a doctor on a date |
| GET | `/appointments/{id}` | Get appointment by ID |
| PATCH | `/appointments/{id}/status` | Update appointment status |
| DELETE | `/appointments/{id}` | Cancel appointment |

---

## Core Concepts

### How Slot Generation Works

A receptionist triggers `POST /slots/generate` for a specific doctor and date. The system looks up the doctor's schedule for that day (from `DoctorSchedule`), divides the working hours into equal intervals based on `consultation_duration_minutes`, and creates individual `Slot` records in the database. For example, a doctor working 09:00–14:00 with 15-minute consultations gets 20 pre-generated slots.

### How Booking Works

Both counter and online bookings use the same slot pool:

- **Counter booking** (`booking_type: counter`) — receptionist picks any slot ID from the available slots list. System auto-assigns.
- **Online booking** (`booking_type: online`) — patient views available slots via `GET /slots/` and picks a specific slot ID.

When a slot is booked, its status changes from `available` to `booked`. Token number equals the slot number.

### How the Waiting List Works

If a patient tries to book a slot that's already taken, they are automatically added to the waiting list with a position number. When any appointment is cancelled, the freed slot is immediately assigned to the first patient in the waiting list (auto-promotion). The waiting list patient gets an appointment created automatically without any manual intervention.

### How the Queue Works

`GET /appointments/queue?doctor_id=X&appointment_date=Y` returns all active appointments for that doctor on that date, ordered by token number. This is the live queue view used by the front desk to call patients.

### Patient UID

Every registered patient gets a unique ID in the format `MED-YYYY-NNNNN` (e.g. `MED-2026-00001`), generated after the database assigns the primary key.

---

## Data Models

```
Doctor
  ├── DoctorSchedule (weekly availability per day)
  └── DoctorLeave (full day or partial leaves)

Patient
  ├── EmergencyContact
  └── MedicalHistory

Slot (pre-generated per doctor per date)
  └── Appointment
        └── WaitingList
```

### Appointment Status Flow

```
BOOKED → CHECKED_IN → CALLED → IN_CONSULTATION → COMPLETED
                                                → INVESTIGATION_PENDING → COMPLETED
       → LATE
       → NO_SHOW
       → CANCELLED
       → RESCHEDULED
```

---

## Design Decisions

**Layered Architecture** — Routers handle HTTP, Services handle business logic, Models handle data. No business logic in routers, no DB queries in routers.

**Soft Delete** — Patients, doctors, and appointments are never hard deleted. `is_active = False` is used throughout to preserve data integrity and history.

**Pre-generated Slots** — Slots are created upfront (not on-demand) so both counter and online users see the same real-time availability. This prevents double-booking at the database level via a unique constraint on `(doctor_id, slot_date, slot_number)`.

**Enum-driven State Machines** — All statuses (appointments, slots, doctors, waiting list) use Python enums backed by PostgreSQL enum types. This prevents invalid state values at both the application and database level.

**Pydantic v2 Validation** — All inputs are validated before hitting the database. Phone numbers, Aadhaar, blood groups, dates, and enums are all validated with custom field validators.

---

## What's Coming Next

- **Phase 2** — JWT Authentication with role-based access control (Admin, Doctor, Receptionist, Patient)
- **Phase 3** — Investigations module (blood tests, X-rays, MRI tracking)
- **Phase 4** — Tests (pytest), API documentation polish, deployment setup

---

## Health Check

```
GET /health
```

```json
{
  "status": "ok",
  "app": "OPD Queue Management API",
  "version": "1.0.0"
}
```