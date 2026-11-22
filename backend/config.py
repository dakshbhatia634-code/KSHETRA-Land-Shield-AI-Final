"""
Backend Configuration for Land Shield AI.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_CHECKPOINT_PATH = BASE_DIR / "data" / "processed" / "models" / "baseline_run" / "best_model.pt"
PREDICTIONS_DIR = BASE_DIR / "data" / "processed" / "predictions"
SAMPLES_DIR = BASE_DIR / "data" / "processed" / "samples"
FRONTEND_DIR = BASE_DIR / "frontend"

PROJECT_NAME = "Land Shield AI"
PROJECT_TAGLINE = "Autonomous Earth Observation & Land Intelligence"
API_V1_PREFIX = "/api"

# Spatial resolution: 10 meters per pixel -> 100 m² per pixel = 0.01 hectares
PIXEL_AREA_HECTARES = 0.01
