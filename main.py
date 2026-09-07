from fastapi import FastAPI
from app.api.v1.ml_ingest import router as ml_router
from app.api.v1.hotspots import router as hotspots_router
from app.api.v1.alerts import router as alerts_router

app = FastAPI(title="CrimeSight API", version="1.0.0")

app.include_router(ml_router, prefix="/api/v1")
app.include_router(hotspots_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "CrimeSight API is running"}