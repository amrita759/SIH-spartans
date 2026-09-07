"""
api/main.py
FastAPI application entry point for SIH26184:
Predictive Cash-Withdrawal Location Intelligence for Cybercrime Complaints.
Theme: Blockchain & Cybersecurity | Ministry of Home Affairs - I4C
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import health, model_info, prediction
from api.services.prediction_service import get_prediction_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up prediction service and load model weights
    print("Pre-loading ML model and indexing engine during application startup...")
    get_prediction_service()
    yield
    print("Application shutting down cleanly.")

app = FastAPI(
    title="SIH26184: Predictive Cash-Withdrawal Location Intelligence Service",
    description=(
        "Production ML and API service forecasting likely fraudulent cash-out locations (ATMs and bank branches) "
        "in advance from cybercrime complaints, enabling proactive law enforcement and banking intervention. "
        "Strictly leakage-free, time-aware, calibrated 0-100 risk scoring with local SHAP explainability."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend / dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router)
app.include_router(model_info.router)
app.include_router(prediction.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
