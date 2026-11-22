"""
Land Shield AI — Main FastAPI Application.

Serves the REST API for real-time satellite land-cover inference,
system health telemetry, and static frontend dashboard assets.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import (
    API_V1_PREFIX,
    FRONTEND_DIR,
    PREDICTIONS_DIR,
    PROJECT_NAME,
    PROJECT_TAGLINE,
    SAMPLES_DIR,
)
from backend.routes.health import router as health_router
from backend.routes.predict import router as predict_router
from backend.routes.geo import router as geo_router
from backend.routes.auth import router as auth_router
from backend.routes.ml_lab import router as ml_router
from backend.routes.imagery import router as imagery_router
from backend.routes.advisor import router as advisor_router
from backend.database import init_database, seed_ml_models_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)
logger = logging.getLogger("land_shield_ai")

# Instantiate FastAPI application
app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_TAGLINE,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local development and web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health_router, prefix=API_V1_PREFIX)
app.include_router(predict_router, prefix=API_V1_PREFIX)
app.include_router(geo_router, prefix=API_V1_PREFIX)
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(ml_router, prefix=API_V1_PREFIX)
app.include_router(imagery_router, prefix=API_V1_PREFIX)
app.include_router(advisor_router, prefix=API_V1_PREFIX)
app.include_router(advisor_router)

IMAGERY_DIR = Path(__file__).resolve().parent.parent / "data" / "processed" / "imagery"
IMAGERY_DIR.mkdir(parents=True, exist_ok=True)

# Ensure output directories exist
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static asset directories
app.mount("/static/predictions", StaticFiles(directory=str(PREDICTIONS_DIR)), name="predictions")
app.mount("/static/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")
app.mount("/static/imagery", StaticFiles(directory=str(IMAGERY_DIR)), name="imagery")

# Mount frontend web dashboard if index.html exists
if FRONTEND_DIR.is_dir() and (FRONTEND_DIR / "index.html").is_file():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
    logger.info("Mounted frontend dashboard from %s", FRONTEND_DIR)
else:
    logger.info("Frontend directory empty or missing index.html; API ready.")


@app.on_event("startup")
async def startup_event():
    logger.info("=== Starting %s Backend ===", PROJECT_NAME)
    init_database()
    seed_ml_models_registry()
    logger.info("Docs available at: /docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
