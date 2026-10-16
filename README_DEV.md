# eTD Builder — local development

## Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `../.env.example` to `../.env` (or `backend/.env`) and set a 32+ character `SECRET_KEY`
4. Run server: `uvicorn app.main:app --reload`
   - Swagger UI: http://127.0.0.1:8000/docs

## Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`
   - Access at http://localhost:5173

## API Proxy
Frontend requests to `/api` are proxied to the backend at port 8000.

## Testing
- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm run test`
- Lint: `cd frontend && npm run lint`

## Database migrations
```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
