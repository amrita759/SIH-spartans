"""
backend/app/main.py
FastAPI application entry point for SIH26184:
Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance.
Theme: Blockchain & Cybersecurity | Ministry of Home Affairs - I4C
"""

import os
import sys
from contextlib import asynccontextmanager

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.core.config import settings
from backend.app.db.repository import init_db
from backend.app.services.prediction_service import get_prediction_service
from backend.app.api.routes import health, model_info, cases, predictions, locations, alerts, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables and seed demo data
    print("[1] Initializing SQLite database and seeding demo cybercrime cases...")
    init_db()
    
    # 2. Pre-warm ML model, transformers, and candidate generator
    print("[2] Pre-loading LightGBM model (v2.0.0), transformers, and ATM indexing engine...")
    get_prediction_service()
    
    yield
    print("[*] Application shutting down cleanly.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production ML and API service forecasting likely fraudulent cash-out locations (ATMs and CRMs) "
        "in advance from cybercrime complaints, enabling proactive law enforcement and banking intervention. "
        "Strictly zero-leakage, time-aware, calibrated 0-100 risk scoring with local TreeSHAP explainability."
    ),
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers (/api/v1/...)
api_v1_prefix = settings.API_V1_STR
app.include_router(health.router, prefix=api_v1_prefix)
app.include_router(model_info.router, prefix=api_v1_prefix)
app.include_router(cases.router, prefix=api_v1_prefix)
app.include_router(predictions.router, prefix=api_v1_prefix)
app.include_router(locations.router, prefix=api_v1_prefix)
app.include_router(alerts.router, prefix=api_v1_prefix)
app.include_router(analytics.router, prefix=api_v1_prefix)

# Also support un-prefixed routes for direct root API calls and orchestrators
app.include_router(health.router)
app.include_router(model_info.router)
app.include_router(cases.router)
app.include_router(predictions.router)
app.include_router(locations.router)
app.include_router(alerts.router)
app.include_router(analytics.router)

@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
