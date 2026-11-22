"""
KSHETRA — LAND SHIELD AI
Machine Learning Lab API Router.

Serves endpoints for classical engineering syllabus ML models:
- Model A: Linear Regression (Vegetation Coverage %)
- Model B: Support Vector Machine (Multi-class Land Cover Classification)
- Model C: K-Nearest Neighbors (Similar Land Finder)
- Model D: DBSCAN (Spatial & Spectral Land Clustering)
- Dataset Explorer & Evaluation Metrics
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.database import get_db_connection

logger = logging.getLogger("kshetra.backend.ml_lab")
router = APIRouter(prefix="/ml", tags=["Machine Learning Lab"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed" / "classical"
MODELS_DIR = DATA_DIR / "models"
REGISTRY_FILE = DATA_DIR / "ml_models_registry.json"
CATALOG_FILE = DATA_DIR / "parcels_catalog.json"
FEATURES_FILE = DATA_DIR / "extracted_features_1500.parquet"

# Global lazy model cache
_MODELS_CACHE = {}


def _get_model(name: str):
    if name not in _MODELS_CACHE:
        model_path = MODELS_DIR / f"{name}.joblib"
        if not model_path.is_file():
            raise HTTPException(status_code=500, detail=f"Model artifact {name}.joblib not found on disk")
        _MODELS_CACHE[name] = joblib.load(model_path)
    return _MODELS_CACHE[name]


# =========================================================================
# Pydantic Request / Response Schemas
# =========================================================================
class LinearPredictRequest(BaseModel):
    mean_red: float = Field(..., ge=0, le=255, description="Mean red band reflectance")
    mean_green: float = Field(..., ge=0, le=255, description="Mean green band reflectance")
    mean_blue: float = Field(..., ge=0, le=255, description="Mean blue band reflectance")
    std_green: Optional[float] = Field(None, ge=0, le=128, description="Green band standard deviation / texture")
    green_red_diff: Optional[float] = None
    brightness: Optional[float] = None


class SVMPredictRequest(BaseModel):
    mean_red: float = Field(..., ge=0, le=255)
    mean_green: float = Field(..., ge=0, le=255)
    mean_blue: float = Field(..., ge=0, le=255)
    std_red: Optional[float] = 15.0
    std_green: Optional[float] = 16.0
    std_blue: Optional[float] = 14.0
    green_red_diff: Optional[float] = None
    brightness: Optional[float] = None
    color_variance: Optional[float] = None


class KNNQueryRequest(BaseModel):
    mean_red: float = Field(..., ge=0, le=255)
    mean_green: float = Field(..., ge=0, le=255)
    mean_blue: float = Field(..., ge=0, le=255)
    vegetation_pct: Optional[float] = Field(None, ge=0, le=100)
    built_up_pct: Optional[float] = Field(None, ge=0, le=100)
    soil_pct: Optional[float] = Field(None, ge=0, le=100)
    k: int = Field(5, ge=1, le=20, description="Number of nearest neighbors")


class DBSCANClusterRequest(BaseModel):
    eps: float = Field(0.45, ge=0.1, le=2.0, description="DBSCAN neighborhood radius (epsilon)")
    min_samples: int = Field(6, ge=2, le=30, description="Minimum points required to form a dense cluster")


# =========================================================================
# Route Handlers
# =========================================================================

@router.get("/models")
async def get_models_overview():
    """Returns the comprehensive registry, metrics, syllabus mapping, and interpretations for all 4 models."""
    if not REGISTRY_FILE.is_file():
        raise HTTPException(status_code=404, detail="ML Models registry not found. Run training script first.")
    with open(REGISTRY_FILE, "r") as f:
        data = json.load(f)
    return data


@router.post("/predict/linear")
async def predict_linear_regression(req: LinearPredictRequest):
    """
    Model A: Linear Regression
    Predicts continuous vegetation coverage percentage from optical reflectance features.
    """
    std_g = req.std_green if req.std_green is not None else 16.5
    diff = req.green_red_diff if req.green_red_diff is not None else (req.mean_green - req.mean_red)
    bright = req.brightness if req.brightness is not None else ((req.mean_red + req.mean_green + req.mean_blue) / 3.0)

    # Features: ["mean_red", "mean_green", "mean_blue", "green_red_diff", "brightness", "std_green"]
    features = np.array([[req.mean_red, req.mean_green, req.mean_blue, diff, bright, std_g]])

    scaler = _get_model("linear_regression_scaler")
    model = _get_model("linear_regression")

    features_scaled = scaler.transform(features)
    pred_val = float(model.predict(features_scaled)[0])
    clipped_val = float(np.clip(pred_val, 0.0, 100.0))

    # Log prediction to SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        pred_id = f"pred_lin_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO ml_predictions (id, model_id, input_features, prediction_result, confidence)
            VALUES (?, 'linear_regression', ?, ?, ?)
        """, (
            pred_id,
            json.dumps(req.dict()),
            json.dumps({"predicted_vegetation_pct": round(clipped_val, 2)}),
            0.85
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("Could not log prediction to DB: %s", e)

    interpretation = "Sparse or barren ground"
    if clipped_val > 60:
        interpretation = "Dense canopy or thriving crops"
    elif clipped_val > 30:
        interpretation = "Moderate healthy vegetation"
    elif clipped_val > 10:
        interpretation = "Scattered scrubland or light grassland"

    return {
        "model": "Linear Regression (OLS)",
        "target": "vegetation_pct",
        "predicted_vegetation_pct": round(clipped_val, 2),
        "unclipped_raw_pct": round(pred_val, 2),
        "layman_summary": f"Estimated greenery is {round(clipped_val, 1)}% ({interpretation}).",
        "scientific_interpretation": interpretation,
        "input_features": {
            "mean_red": req.mean_red,
            "mean_green": req.mean_green,
            "mean_blue": req.mean_blue,
            "green_red_diff": round(diff, 2),
            "brightness": round(bright, 2),
            "std_green": round(std_g, 2)
        },
        "model_confidence": "Evaluated R² = 0.195, MAE = ±7.65% across 1,500 real satellite tiles."
    }


@router.post("/predict/svm")
async def predict_svm(req: SVMPredictRequest):
    """
    Model B: Support Vector Machine (RBF Kernel)
    Classifies land cover into one of 7 verified ground truth classes with calibrated probabilities.
    """
    std_r = req.std_red if req.std_red is not None else 15.0
    std_g = req.std_green if req.std_green is not None else 16.0
    std_b = req.std_blue if req.std_blue is not None else 14.0
    diff = req.green_red_diff if req.green_red_diff is not None else (req.mean_green - req.mean_red)
    bright = req.brightness if req.brightness is not None else ((req.mean_red + req.mean_green + req.mean_blue) / 3.0)
    c_var = req.color_variance if req.color_variance is not None else ((std_r**2 + std_g**2 + std_b**2) / 3.0)

    # Features: ["mean_red", "mean_green", "mean_blue", "std_red", "std_green", "std_blue", "green_red_diff", "brightness", "color_variance"]
    features = np.array([[
        req.mean_red, req.mean_green, req.mean_blue,
        std_r, std_g, std_b,
        diff, bright, c_var
    ]])

    scaler = _get_model("svm_scaler")
    model = _get_model("svm_classifier")

    features_scaled = scaler.transform(features)
    pred_class_id = int(model.predict(features_scaled)[0])
    probabilities = model.predict_proba(features_scaled)[0]

    class_labels = {
        0: "Water Bodies",
        1: "Trees & Canopy",
        2: "Flooded Vegetation",
        3: "Crops & Agriculture",
        4: "Built-up & Urban",
        5: "Bare Soil",
        6: "Reflective / Other"
    }

    # Format probability distribution
    prob_dist = {}
    for c_id, prob in zip(model.classes_, probabilities):
        label_name = class_labels.get(int(c_id), f"Class {c_id}")
        prob_dist[label_name] = round(float(prob) * 100.0, 1)

    predicted_label = class_labels.get(pred_class_id, "Unknown")
    confidence_score = float(np.max(probabilities))

    # Log prediction to SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        pred_id = f"pred_svm_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO ml_predictions (id, model_id, input_features, prediction_result, confidence)
            VALUES (?, 'svm_classifier', ?, ?, ?)
        """, (
            pred_id,
            json.dumps(req.dict()),
            json.dumps({"predicted_class": predicted_label, "confidence": round(confidence_score, 3)}),
            confidence_score
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("Could not log prediction to DB: %s", e)

    return {
        "model": "Support Vector Machine (RBF Kernel)",
        "predicted_class_id": pred_class_id,
        "predicted_class_name": predicted_label,
        "confidence_pct": round(confidence_score * 100.0, 1),
        "layman_summary": f"This land is classified as {predicted_label} with {round(confidence_score * 100.0, 1)}% probability.",
        "class_probabilities": prob_dist,
        "model_accuracy": "Evaluated Test Accuracy: 71.67%, Weighted F1: 0.683 across 300 held-out test parcels."
    }


@router.post("/knn/neighbors")
async def find_knn_neighbors(req: KNNQueryRequest):
    """
    Model C: K-Nearest Neighbors (KNN)
    Finds the top K most similar verified parcels across India using multi-dimensional Euclidean distance.
    """
    if not CATALOG_FILE.is_file():
        raise HTTPException(status_code=404, detail="Parcels catalog not found on disk")

    with open(CATALOG_FILE, "r") as f:
        catalog = json.load(f)

    # Defaults if percentages not provided
    v_pct = req.vegetation_pct if req.vegetation_pct is not None else 35.0
    b_pct = req.built_up_pct if req.built_up_pct is not None else 10.0
    s_pct = req.soil_pct if req.soil_pct is not None else 45.0
    diff = req.mean_green - req.mean_red
    bright = (req.mean_red + req.mean_green + req.mean_blue) / 3.0

    # Query vector: ["mean_red", "mean_green", "mean_blue", "green_red_diff", "brightness", "vegetation_pct", "built_up_pct", "soil_pct"]
    query_vec = np.array([[
        req.mean_red, req.mean_green, req.mean_blue,
        diff, bright,
        v_pct, b_pct, s_pct
    ]])

    scaler = _get_model("knn_scaler")
    model = _get_model("knn_model")

    query_scaled = scaler.transform(query_vec)
    distances, indices = model.kneighbors(query_scaled, n_neighbors=req.k)

    neighbors = []
    for dist, idx in zip(distances[0], indices[0]):
        parcel = catalog[idx]
        # Similarity formula: 100 / (1 + distance)
        sim_pct = round(100.0 / (1.0 + float(dist)), 1)
        neighbors.append({
            "parcel_id": parcel["id"],
            "latitude": parcel["lat"],
            "longitude": parcel["lon"],
            "similarity_pct": sim_pct,
            "euclidean_distance": round(float(dist), 3),
            "dominant_land_type": parcel["dominant_class"],
            "vegetation_pct": parcel["vegetation_pct"],
            "built_up_pct": parcel["built_up_pct"],
            "soil_pct": parcel["soil_pct"],
            "water_pct": parcel["water_pct"],
            "brightness": parcel["brightness"]
        })

    return {
        "model": "K-Nearest Neighbors (KNN)",
        "k_requested": req.k,
        "total_catalog_size": len(catalog),
        "neighbors": neighbors,
        "layman_summary": f"Found {len(neighbors)} real parcels in India with matching environmental and spectral conditions."
    }


@router.post("/dbscan/cluster")
async def cluster_dbscan(req: DBSCANClusterRequest):
    """
    Model D: DBSCAN Clustering
    Runs density-based spatial clustering on genuine Indian survey points and satellite features.
    """
    if not FEATURES_FILE.is_file():
        raise HTTPException(status_code=404, detail="Extracted features file not found")

    df = pd.read_parquet(FEATURES_FILE)
    dbscan_features = ["latitude", "longitude", "vegetation_pct", "built_up_pct"]
    X = df[dbscan_features].values

    scaler = _get_model("dbscan_scaler")
    X_scaled = scaler.transform(X)

    from sklearn.cluster import DBSCAN as SK_DBSCAN
    db = SK_DBSCAN(eps=req.eps, min_samples=req.min_samples)
    labels = db.fit_predict(X_scaled)

    df["cluster"] = labels
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int(np.sum(labels == -1))

    class_labels = {
        0: "Water Bodies", 1: "Trees & Canopy", 2: "Flooded Veg",
        3: "Crops", 4: "Built-up", 5: "Bare Soil", 6: "Reflective"
    }

    cluster_summaries = {}
    for c_id in sorted(list(set(labels))):
        c_df = df[df["cluster"] == c_id]
        c_name = f"Cluster #{c_id}" if c_id != -1 else "Spectral Anomalies / Outliers"
        dominant_cls_id = int(c_df["dominant_class"].mode()[0]) if len(c_df) > 0 else 5
        cluster_summaries[c_name] = {
            "cluster_id": int(c_id),
            "size": len(c_df),
            "pct_of_dataset": round(len(c_df) / len(df) * 100, 1),
            "avg_vegetation_pct": round(float(c_df["vegetation_pct"].mean()), 1),
            "avg_built_up_pct": round(float(c_df["built_up_pct"].mean()), 1),
            "avg_soil_pct": round(float(c_df["soil_pct"].mean()), 1),
            "center_lat": round(float(c_df["latitude"].mean()), 4),
            "center_lon": round(float(c_df["longitude"].mean()), 4),
            "dominant_land_type": class_labels.get(dominant_cls_id, "Mixed")
        }

    # Downsampled preview points for chart
    preview_points = []
    for idx, row in df.head(100).iterrows():
        preview_points.append({
            "sample_id": int(row["sample_id"]),
            "lat": round(float(row["latitude"]), 4),
            "lon": round(float(row["longitude"]), 4),
            "vegetation_pct": round(float(row["vegetation_pct"]), 1),
            "built_up_pct": round(float(row["built_up_pct"]), 1),
            "cluster": int(row["cluster"])
        })

    return {
        "model": "DBSCAN Clustering",
        "parameters": {"eps": req.eps, "min_samples": req.min_samples},
        "clusters_discovered": n_clusters,
        "noise_points": n_noise,
        "noise_pct": round(n_noise / len(df) * 100, 1),
        "total_samples": len(df),
        "clusters": cluster_summaries,
        "scatter_preview": preview_points,
        "layman_summary": f"Discovered {n_clusters} distinct land zones across India with {n_noise} unique anomaly parcels."
    }


@router.get("/dataset")
async def get_dataset_samples(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    dominant_class: Optional[int] = None
):
    """
    Dataset Explorer:
    Streams paginated genuine Sentinel-2 multi-spectral samples used in training.
    """
    if not FEATURES_FILE.is_file():
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_parquet(FEATURES_FILE)
    if dominant_class is not None:
        df = df[df["dominant_class"] == dominant_class]

    total = len(df)
    page_df = df.iloc[offset: offset + limit]

    class_labels = {
        0: "Water Bodies", 1: "Trees & Canopy", 2: "Flooded Veg",
        3: "Crops", 4: "Built-up", 5: "Bare Soil", 6: "Reflective"
    }

    records = []
    for _, row in page_df.iterrows():
        records.append({
            "sample_id": int(row["sample_id"]),
            "latitude": round(float(row["latitude"]), 4),
            "longitude": round(float(row["longitude"]), 4),
            "mean_red": round(float(row["mean_red"]), 1),
            "mean_green": round(float(row["mean_green"]), 1),
            "mean_blue": round(float(row["mean_blue"]), 1),
            "vegetation_pct": round(float(row["vegetation_pct"]), 1),
            "built_up_pct": round(float(row["built_up_pct"]), 1),
            "soil_pct": round(float(row["soil_pct"]), 1),
            "water_pct": round(float(row["water_pct"]), 1),
            "dominant_class": class_labels.get(int(row["dominant_class"]), "Unknown"),
            "dominant_class_id": int(row["dominant_class"])
        })

    return {
        "total_records": total,
        "limit": limit,
        "offset": offset,
        "records": records
    }
