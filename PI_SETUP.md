# eTD Builder — Raspberry Pi (runtime) package

This repo is the **Pi / always-on** slice of eTD Builder (no MinerU).

## On the Pi (TigerVNC terminal)

```bash
git clone https://github.com/Gagan-V-Sha/M.git
cd M
cp .env.runtime.example .env
# edit .env: SECRET_KEY, POSTGRES_PASSWORD, DATABASE_URL

# Postgres (LAN-visible for workstation scans)
docker compose -f docker-compose.yml -f docker-compose.shared-db.yml up -d db

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-runtime.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend (another terminal):

```bash
cd frontend
npm install
npm run build
# serve dist/ or use your static server / nginx
```

Env must include:
- `ROLE=runtime`
- `MINERU_ENABLED=false`
- `DATABASE_URL=postgresql://gspr:PASSWORD@127.0.0.1:5432/gspr_db`

Workstation (separate machine) points at the Pi LAN IP with `MINERU_ENABLED=true` and the same Postgres password.
