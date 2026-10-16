# eTD Builder: Automated Medical Device Technical Documentation

eTD Builder is a comprehensive full-stack application designed to automate the creation and management of Electronic Technical Documentation (eTD) for medical device manufacturers. It specifically focuses on ensuring compliance with the EU Medical Device Regulation (MDR 2017/745), particularly the General Safety and Performance Requirements (GSPR) listed in Annex I.

The system allows to define device profiles, automatically suggests applicable standards, extracts GSPR mappings from PDF documents, and manages evidence for compliance audits.


## Key Features

- Device Profile Management: Define device characteristics (e.g., sterile, electrical, software) to determine regulatory scope.
- Intelligent Standard Suggestion: A rules-based engine that recommends harmonized standards..
- Automated Data Extraction: Integration with MinerU for extracting GSPR-to-Clause mappings from technical standards (PDF).
- Compliance Dashboard: Real-time status tracking for Annex I requirements.
- Evidence Management: Linking technical documents directly to regulatory requirements.



## Backend Architecture

The backend is built with FastAPI under `backend/app/`. Start it with:

```bash
cd backend
uvicorn app.main:app --reload
```

### Core (`app/core/`)
- `database.py`: SQLAlchemy engine, sessions, and table creation.
- `models.py`: ORM models (Users, Standards, GSPR Requirements, Device Profiles, etc.).
- `datatypes.py`: Pydantic schemas for request/response validation.

### Security (`app/security/`)
- `auth.py`: JWT authentication, password hashing, and route dependencies.

### Features (`app/features/`)
- `etd/routes.py`: eTD editor — applicability, notes, evidence linking, PDF export.
- `importer/routes.py` + `service.py`: Document upload and MinerU PDF parsing.
- `importer/standard_parser.py`: GSPR-to-standard mapping extraction logic.

Schema changes should go through Alembic (`backend/alembic`). One-off seed scripts live in `backend/scripts/setup/`.

## Frontend Architecture

The frontend is a React + Vite app under `frontend/src/` using a presenter/view pattern:

- `dashboard/`: Device list and compliance overview.
- `documents/` and `features/etd/`: GSPR eTD editor and chapter modules.
- `database/`: Master data viewer for standards, GSPRs, and evidence.
- `auth/`: Login, signup, MFA, and password reset flows.
- `layout/`: Navbar, sidebar, and main layout shell.
- `communication/axios.js`: API client with auth interceptors.

## Tech Stack

- Backend: FastAPI (Python), SQLAlchemy ORM, Pydantic, SlowAPI.
- Frontend: React, Vite, CSS (Vanilla).
- Database: SQLite (default) or any SQLAlchemy-supported RDBMS.
- Extraction: MinerU (PDF processing).
- Playwright(Chromium) for PDF export.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### Installation

1. Copy .env.example to .env and configure your SECRET_KEY.
2. Setup Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. Setup Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. Optional Windows launcher: `run_project.bat` (or `scripts\dev\run_project.bat`).


## Security and Deployment

- Rate Limiting: Authentication routes are limited to 5 requests per minute to prevent brute-force attacks.
- Audit Logging: Every sensitive action (login, logout, data update) is recorded in the `audit_log` table with user ID, action, and IP address.
- Deployment: A `docker-compose.yml` file is provided for quick containerized deployment.

### Runtime vs scanner (Pi + workstation)

Same codebase, two profiles. **Step 1** = optional MinerU. **Step 2** = shared Postgres.

| Host | Install | Env file |
|---|---|---|
| Raspberry Pi (always-on) | `pip install -r requirements-runtime.txt` | copy `.env.runtime.example` → `.env` |
| Workstation (scans) | `pip install -r requirements-scanner.txt` | copy `.env.scanner.example` → `.env` |

**On the Pi — start shared Postgres (LAN-visible):**
```bash
docker compose -f docker-compose.yml -f docker-compose.shared-db.yml up -d db
```
Then start the app with `ROLE=runtime` `MINERU_ENABLED=false` and  
`DATABASE_URL=postgresql://gspr:PASSWORD@127.0.0.1:5432/gspr_db`.

**On the workstation** use the **same password** and the Pi’s LAN IP:  
`DATABASE_URL=postgresql://gspr:PASSWORD@PI_LAN_IP:5432/gspr_db` with `MINERU_ENABLED=true`.

Check connectivity (no password printed):
```bash
cd backend
python scripts/check_shared_db.py
```

- `GET /config` → `mineru_ready`, `database_backend`, `database_shared`.
- Scan on workstation → rows land in Postgres → Pi users see mappings on refresh.
- Do **not** copy SQLite files between machines when using shared Postgres.


