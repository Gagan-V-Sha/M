# Test suites for eTD Builder (MDR / GSPR technical documentation)

This folder is the map of automated tests. The runnable files live with each stack so pytest and Vitest keep their normal working directories.

```
backend/tests/
  conftest.py                 shared API client, DB, users
  auth/                       register, login, lockout, MFA, GDPR
  security/                   access control
  api/                        GSPR, eTD RBAC, devices, standards/evidence
  imports/                    PDF / CSV import
  unit/                       password hashing, text helpers

frontend/tests/
  App.test.jsx                route guards
  auth/                       login, signup, forgot password, MFA
  layout/                     navbar, sidebar (active page)
  dashboard/
  documents/                  eTD editor
  database/                   Database Viewer
  settings/
  communication/              axios auth headers
```

## Run backend

```powershell
cd backend
.\.venv\Scripts\activate
pytest
```

## Run frontend

```powershell
cd frontend
npm test
```

CI (`.github/workflows/ci-cd.yml`) runs both of these jobs.
