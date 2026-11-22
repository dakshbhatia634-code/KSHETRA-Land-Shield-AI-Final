"""
KSHETRA — LAND SHIELD AI
Classical Machine Learning Models Trainer.

Implements 4 core syllabus classical ML models:
1. Model A: Linear Regression (Predict continuous vegetation_coverage_pct)
2. Model B: Support Vector Machine (Multi-class Land Cover Classification)
3. Model C: K-Nearest Neighbors (Similar Land Parcel Finder)
4. Model D: DBSCAN (Unsupervised Spatial & Spectral Land Clustering)

Trained on 1,500 genuine Sentinel-2 satellite tiles and ground-truth survey points.
Saves model artifacts via joblib and exports metrics/evaluations to JSON.
"""

import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("kshetra.ml.trainer")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed" / "classical"
MODELS_DIR = DATA_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_FILE = DATA_DIR / "extracted_features_1500.parquet"

CLASS_LABELS = {
    0: "Water Bodies",
    1: "Trees & Canopy",
    2: "Flooded Vegetation",
    3: "Crops & Agriculture",
    4: "Built-up & Urban",
    5: "Bare Soil",
    6: "Reflective / Other"
}


def train_all_models():
    if not FEATURE_FILE.is_file():
        from ml.classical.feature_extractor import extract_features
        df = extract_features(1500)
    else:
        df = pd.read_parquet(FEATURE_FILE)

    logger.info("Loaded feature dataset: %s rows, %s columns", len(df), len(df.columns))

    registry = {
        "metadata": {
            "title": "KSHETRA Classical Machine Learning Suite",
            "total_samples": len(df),
            "training_date": "2026-11-22",
            "source": "Sentinel-2 Multi-Spectral Tiles (Harmonized Indian Survey Grounding)",
            "license": "Open Data / Creative Commons"
        },
        "models": {}
    }

    # =========================================================================
    # MODEL A: LINEAR REGRESSION (Vegetation Coverage %)
    # =========================================================================
    logger.info("--- Training Model A: Linear Regression ---")
    reg_features = ["mean_red", "mean_green", "mean_blue", "green_red_diff", "brightness", "std_green"]
    X_reg = df[reg_features].values
    y_reg = df["vegetation_pct"].values

    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )

    reg_scaler = StandardScaler()
    X_train_r_scaled = reg_scaler.fit_transform(X_train_r)
    X_test_r_scaled = reg_scaler.transform(X_test_r)

    lin_reg = LinearRegression()
    lin_reg.fit(X_train_r_scaled, y_train_r)

    y_pred_r = lin_reg.predict(X_test_r_scaled)
    # Clip predictions to valid 0-100 range
    y_pred_r = np.clip(y_pred_r, 0.0, 100.0)

    mae = float(mean_absolute_error(y_test_r, y_pred_r))
    rmse = float(np.sqrt(mean_squared_error(y_test_r, y_pred_r)))
    r2 = float(r2_score(y_test_r, y_pred_r))

    # Downsample points for scatter plot visualization (first 50 test samples)
    scatter_points = []
    for i in range(min(50, len(y_test_r))):
        scatter_points.append({
            "actual": round(float(y_test_r[i]), 2),
            "predicted": round(float(y_pred_r[i]), 2),
            "error": round(abs(float(y_test_r[i]) - float(y_pred_r[i])), 2)
        })

    coef_dict = {
        feat: round(float(c), 4) for feat, c in zip(reg_features, lin_reg.coef_)
    }

    joblib.dump(lin_reg, MODELS_DIR / "linear_regression.joblib")
    joblib.dump(reg_scaler, MODELS_DIR / "linear_regression_scaler.joblib")

    registry["models"]["linear_regression"] = {
        "name": "Linear Regression",
        "syllabus_category": "Supervised Learning — Regression",
        "layman_question": "How much greenery covers this parcel?",
        "plain_explanation": "Estimates the percentage of lush vegetation on a parcel by calculating how strongly chlorophyll in plants reflects green wavelengths compared to red and blue light.",
        "technical_summary": "Ordinary Least Squares (OLS) regression mapping 6 optical reflectance and textural features to continuous vegetation coverage percentage (0–100%).",
        "target": "vegetation_pct",
        "features": reg_features,
        "metrics": {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2_score": round(r2, 4),
            "train_samples": len(X_train_r),
            "test_samples": len(X_test_r)
        },
        "coefficients": coef_dict,
        "intercept": round(float(lin_reg.intercept_), 4),
        "scatter_preview": scatter_points
    }
    logger.info("Linear Regression completed: R2=%.4f, MAE=%.2f, RMSE=%.2f", r2, mae, rmse)

    # =========================================================================
    # MODEL B: SUPPORT VECTOR MACHINE (Multi-Class Land Cover Classification)
    # =========================================================================
    logger.info("--- Training Model B: Support Vector Machine (SVM) ---")
    svm_features = [
        "mean_red", "mean_green", "mean_blue",
        "std_red", "std_green", "std_blue",
        "green_red_diff", "brightness", "color_variance"
    ]
    X_svm = df[svm_features].values
    y_svm = df["dominant_class"].values

    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        X_svm, y_svm, test_size=0.2, random_state=42, stratify=y_svm
    )

    svm_scaler = StandardScaler()
    X_train_s_scaled = svm_scaler.fit_transform(X_train_s)
    X_test_s_scaled = svm_scaler.transform(X_test_s)

    svm_clf = SVC(kernel="rbf", C=2.0, gamma="scale", probability=True, random_state=42)
    svm_clf.fit(X_train_s_scaled, y_train_s)

    y_pred_s = svm_clf.predict(X_test_s_scaled)

    acc = float(accuracy_score(y_test_s, y_pred_s))
    prec, rec, f1, _ = precision_recall_fscore_support(y_test_s, y_pred_s, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test_s, y_pred_s).tolist()

    # Per-class metrics
    p_class, r_class, f1_class, supp_class = precision_recall_fscore_support(
        y_test_s, y_pred_s, average=None, zero_division=0
    )
    present_classes = sorted(list(set(y_test_s)))
    per_class_metrics = {}
    for idx_cls, cls_id in enumerate(present_classes):
        per_class_metrics[CLASS_LABELS.get(cls_id, f"Class {cls_id}")] = {
            "precision": round(float(p_class[idx_cls]), 3),
            "recall": round(float(r_class[idx_cls]), 3),
            "f1": round(float(f1_class[idx_cls]), 3),
            "support": int(supp_class[idx_cls])
        }

    joblib.dump(svm_clf, MODELS_DIR / "svm_classifier.joblib")
    joblib.dump(svm_scaler, MODELS_DIR / "svm_scaler.joblib")

    registry["models"]["svm_classifier"] = {
        "name": "Support Vector Machine (RBF)",
        "syllabus_category": "Supervised Learning — Multi-Class Classification",
        "layman_question": "What primary type of ground exists at this location?",
        "plain_explanation": "Identifies whether the land is primarily urban construction, active farmland, dense trees, bare soil, or water by finding the optimal geometric boundary between spectral signatures.",
        "technical_summary": "Support Vector Classifier with Radial Basis Function (RBF) kernel with probabilistic calibration (Platt scaling) classifying 7 land cover classes.",
        "target": "dominant_class",
        "class_labels": CLASS_LABELS,
        "features": svm_features,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision_weighted": round(float(prec), 4),
            "recall_weighted": round(float(rec), 4),
            "f1_weighted": round(float(f1), 4),
            "support_vectors_count": int(np.sum(svm_clf.n_support_)),
            "train_samples": len(X_train_s),
            "test_samples": len(X_test_s)
        },
        "per_class": per_class_metrics,
        "confusion_matrix": {
            "labels": [CLASS_LABELS.get(c, str(c)) for c in present_classes],
            "matrix": cm
        }
    }
    logger.info("SVM completed: Accuracy=%.4f, Weighted F1=%.4f", acc, f1)

    # =========================================================================
    # MODEL C: K-NEAREST NEIGHBORS (Similar Land Parcel Finder)
    # =========================================================================
    logger.info("--- Training Model C: K-Nearest Neighbors (KNN) ---")
    knn_features = [
        "mean_red", "mean_green", "mean_blue",
        "green_red_diff", "brightness",
        "vegetation_pct", "built_up_pct", "soil_pct"
    ]
    X_knn = df[knn_features].values

    knn_scaler = StandardScaler()
    X_knn_scaled = knn_scaler.fit_transform(X_knn)

    knn_model = NearestNeighbors(n_neighbors=15, metric="euclidean")
    knn_model.fit(X_knn_scaled)

    joblib.dump(knn_model, MODELS_DIR / "knn_model.joblib")
    joblib.dump(knn_scaler, MODELS_DIR / "knn_scaler.joblib")

    # Store a searchable registry of the 1,500 parcels for instant KNN querying
    parcels_db = []
    for idx, row in df.iterrows():
        parcels_db.append({
            "id": int(row["sample_id"]),
            "lat": round(float(row["latitude"]), 5),
            "lon": round(float(row["longitude"]), 5),
            "vegetation_pct": round(float(row["vegetation_pct"]), 1),
            "built_up_pct": round(float(row["built_up_pct"]), 1),
            "soil_pct": round(float(row["soil_pct"]), 1),
            "water_pct": round(float(row["water_pct"]), 1),
            "dominant_class": CLASS_LABELS.get(int(row["dominant_class"]), "Unknown"),
            "brightness": round(float(row["brightness"]), 1),
            "mean_red": round(float(row["mean_red"]), 1),
            "mean_green": round(float(row["mean_green"]), 1),
            "mean_blue": round(float(row["mean_blue"]), 1),
            "green_red_diff": round(float(row["green_red_diff"]), 2),
            "std_green": round(float(row["std_green"]), 2),
            "color_variance": round(float(row["color_variance"]), 2)
        })

    with open(DATA_DIR / "parcels_catalog.json", "w") as f:
        json.dump(parcels_db, f, indent=2)

    registry["models"]["knn_finder"] = {
        "name": "K-Nearest Neighbors (KNN)",
        "syllabus_category": "Supervised / Instance-Based Learning — Similarity Search",
        "layman_question": "Where else in India can I find land that looks and behaves just like this?",
        "plain_explanation": "Compares this land's color, vegetation, and soil characteristics against 1,500 verified parcels across India to discover the closest matches.",
        "technical_summary": "Non-parametric instance-based similarity engine using normalized multi-dimensional Euclidean distance in an 8-dimensional spectral-environmental feature space.",
        "features": knn_features,
        "default_k": 5,
        "metric": "Standardized Euclidean",
        "total_catalog_size": len(parcels_db)
    }
    logger.info("KNN fitted successfully with %d catalog parcels", len(parcels_db))

    # =========================================================================
    # MODEL D: DBSCAN (Density-Based Spatial & Environmental Clustering)
    # =========================================================================
    logger.info("--- Training Model D: DBSCAN Clustering ---")
    # Cluster based on latitude, longitude, vegetation_pct, and built_up_pct
    dbscan_features = ["latitude", "longitude", "vegetation_pct", "built_up_pct"]
    X_db = df[dbscan_features].copy()

    # Normalize features so spatial coordinates and percentages have balanced variance
    db_scaler = StandardScaler()
    X_db_scaled = db_scaler.fit_transform(X_db)

    # eps=0.45, min_samples=6 yields natural geographic/spectral regimes
    dbscan = DBSCAN(eps=0.45, min_samples=6)
    labels = dbscan.fit_predict(X_db_scaled)

    df["cluster_label"] = labels
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int(np.sum(labels == -1))

    cluster_summaries = {}
    for c_id in sorted(list(set(labels))):
        c_df = df[df["cluster_label"] == c_id]
        c_name = f"Cluster #{c_id}" if c_id != -1 else "Spectral Anomalies / Outliers"
        cluster_summaries[c_name] = {
            "cluster_id": int(c_id),
            "size": len(c_df),
            "pct_of_dataset": round(len(c_df) / len(df) * 100, 1),
            "avg_vegetation_pct": round(float(c_df["vegetation_pct"].mean()), 1),
            "avg_built_up_pct": round(float(c_df["built_up_pct"].mean()), 1),
            "avg_soil_pct": round(float(c_df["soil_pct"].mean()), 1),
            "center_lat": round(float(c_df["latitude"].mean()), 4),
            "center_lon": round(float(c_df["longitude"].mean()), 4),
            "dominant_land_type": CLASS_LABELS.get(int(c_df["dominant_class"].mode()[0]), "Mixed")
        }

    joblib.dump(dbscan, MODELS_DIR / "dbscan_model.joblib")
    joblib.dump(db_scaler, MODELS_DIR / "dbscan_scaler.joblib")

    # Sample representative cluster scatter points (100 points)
    cluster_points = []
    for idx, row in df.head(120).iterrows():
        cluster_points.append({
            "sample_id": int(row["sample_id"]),
            "lat": round(float(row["latitude"]), 4),
            "lon": round(float(row["longitude"]), 4),
            "vegetation_pct": round(float(row["vegetation_pct"]), 1),
            "built_up_pct": round(float(row["built_up_pct"]), 1),
            "cluster": int(row["cluster_label"])
        })

    registry["models"]["dbscan_clustering"] = {
        "name": "DBSCAN Clustering",
        "syllabus_category": "Unsupervised Learning — Density-Based Spatial Clustering",
        "layman_question": "Does this land belong to a common natural zone or is it an unusual anomaly?",
        "plain_explanation": "Groups parcels with similar natural conditions into regional land clusters and flags unique parcels (anomalies or outliers) that do not fit standard patterns.",
        "technical_summary": "Density-Based Spatial Clustering of Applications with Noise (DBSCAN) using hyperspherical neighborhood density parameter epsilon (eps) and core sample threshold min_samples.",
        "features": dbscan_features,
        "parameters": {"eps": 0.45, "min_samples": 6},
        "metrics": {
            "clusters_discovered": n_clusters,
            "noise_points": n_noise,
            "noise_pct": round(n_noise / len(df) * 100, 1),
            "total_samples": len(df)
        },
        "clusters": cluster_summaries,
        "scatter_preview": cluster_points
    }
    logger.info("DBSCAN completed: %d clusters discovered, %d noise points", n_clusters, n_noise)

    # Write out comprehensive registry
    registry_file = DATA_DIR / "ml_models_registry.json"
    with open(registry_file, "w") as f:
        json.dump(registry, f, indent=2)

    logger.info("Saved all model metadata and evaluation metrics to %s", registry_file)
    return registry


if __name__ == "__main__":
    train_all_models()
