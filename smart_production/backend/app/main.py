"""
Smart_Production API — FastAPI backend.

Run locally:
    uvicorn app.main:app --reload --port 8000

Docs (auto-generated): http://localhost:8000/docs
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import machines, sensors, alerts, maintenance, dashboard, erp, predict

# Creates tables on startup if they don't exist yet.
# For production schema changes, use Alembic migrations instead
# (see backend/README.md).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart_Production API",
    description="Manufacturing analytics backend — real DB, real ML predictions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,https://smart-production-phi.vercel.app",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(machines.router)
app.include_router(sensors.router)
app.include_router(alerts.router)
app.include_router(maintenance.router)
app.include_router(dashboard.router)
app.include_router(erp.router)
app.include_router(predict.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
