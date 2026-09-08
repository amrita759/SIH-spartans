# SIH26184 Backend Service

Production FastAPI and Machine Learning integration service for forecasting likely cybercrime cash-withdrawal locations in advance.

## Architecture
- **Framework**: FastAPI (Pydantic v2, Python 3.13)
- **ML Model**: LightGBM Classifier (`artifacts/model/model_v1.0.0.joblib`)
- **Explainability**: TreeSHAP with operational LEA factor descriptions
- **Database**: SQLite (`sih26184.db`) via SQLAlchemy ORM
- **Spatial Master**: 137,444 Indian ATMs/CRMs indexed across all states and districts

## Quick Start
```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Run service
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
Swagger UI will be available at `http://localhost:8000/docs`.
