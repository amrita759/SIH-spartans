# SIH26184 Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies (libgomp for LightGBM OpenMP support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source, configs, artifacts, and indexed data
COPY configs/ ./configs/
COPY src/ ./src/
COPY api/ ./api/
COPY artifacts/ ./artifacts/
COPY data/processed/ ./data/processed/

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Start FastAPI prediction service
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
