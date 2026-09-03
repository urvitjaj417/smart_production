# Smart_Production

A manufacturing analytics platform: real-time sensor monitoring, ML-based
predictive maintenance, and an executive dashboard — built on a proper
React + FastAPI + PostgreSQL stack.

This replaces the earlier single-file HTML prototype (`smart_production_v6_2.html`)
with a real backend, real database, and a real trained ML model, per the
project spec.

## Stack

| Layer      | Tech                                      |
|------------|--------------------------------------------|
| Frontend   | React + TypeScript + Tailwind CSS + Chart.js |
| Backend    | FastAPI (Python)                          |
| Database   | PostgreSQL                                |
| ML         | scikit-learn (RandomForest, two-stage: fault detection + fault-type classification) |
| Deployment | Docker, GitHub Actions CI, Vercel (frontend) + Render/Railway (backend+DB) |

## Project layout

```
smart_production/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + router registration
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # ORM tables (machines, sensor_readings, alerts, ...)
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── routers/           # machines, sensors, alerts, maintenance, dashboard, erp, predict
│   │   └── ml/
│   │       ├── train_model.py # Trains the RandomForest model
│   │       └── predict.py     # Loads model, serves inference
│   ├── seed.py                 # Populates DB with demo machines + 30 days of history
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.ts      # Typed API client (axios)
│   │   ├── components/        # KpiCard, etc.
│   │   ├── pages/Dashboard.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Quick start (Docker — recommended)

```bash
docker compose up --build
```

This starts Postgres, trains the ML model, boots the FastAPI backend on
`:8000`, and serves the built frontend on `:5173`. Then seed the database:

```bash
docker compose exec backend python seed.py
```

Visit `http://localhost:5173`. API docs (Swagger UI) at `http://localhost:8000/docs`.

## Local development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL if not using the default local Postgres
python -m app.ml.train_model     # trains model.joblib
python seed.py                   # populate demo data (requires Postgres running)
uvicorn app.main:app --reload --port 8000
```

You'll need a local Postgres instance matching `.env`'s `DATABASE_URL`, e.g.:
```bash
docker run -d -p 5432:5432 -e POSTGRES_USER=smart_production \
  -e POSTGRES_PASSWORD=smart_production -e POSTGRES_DB=smart_production postgres:16-alpine
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173, proxies /api to :8000
```

## Deployment

- **Frontend → Vercel**: connect the repo, set root directory to `frontend/`,
  build command `npm run build`, output directory `dist`. Set `VITE_API_URL`
  to the deployed backend origin, for example
  `https://your-backend.onrender.com` (without `/api`). The frontend uses the
  Vite `/api` proxy only during local development.
- **Backend + DB → Render or Railway**: both support "deploy from Dockerfile"
  plus a managed Postgres add-on — point `DATABASE_URL` at the managed
  instance's connection string and set `CORS_ORIGINS` to the Vercel origin,
  for example `https://smart-production-phi.vercel.app`.
- **CI**: `.github/workflows/ci.yml` runs on every push/PR — trains the model
  as a smoke test and type-checks + builds the frontend.

## Retraining the ML model on real data

`train_model.py` currently trains on synthetic data (see
`generate_synthetic_training_data()`) so the project is runnable without
historical data. Once you have real logged faults in `sensor_readings`,
switch to real data:

```python
from app.ml.train_model import train
train(use_db=True)
```

## What's real vs. what's still a stub

Being upfront, matching the honesty standard used throughout this project:

- **Real**: sensor ingestion, KPI aggregation (SQL), the RandomForest
  fault-detection/fault-type model, alerts, maintenance logging, machine CRUD.
- **Partial**: the React frontend currently ships one page (Executive
  Dashboard) as a working reference implementation — Failures, Sensors, OEE,
  Correlation, etc. from the original HTML prototype aren't ported yet.
  `App.tsx`'s `navItems` array is where to add them.
- **Not real / needs real integration**: ERP/Supply Chain data model exists
  (inventory, vendors, purchase orders tables + CRUD endpoints) but isn't
  connected to an actual ERP system — same honest caveat as the HTML prototype.
