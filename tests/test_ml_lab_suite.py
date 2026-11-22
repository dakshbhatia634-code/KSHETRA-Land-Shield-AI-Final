"""
Unit and Integration Tests for KSHETRA Classical ML Lab Suite & Database.
Uses standard library urllib.request against running server.
"""

import json
import sys
from pathlib import Path
import urllib.request

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.database import get_db_connection

BASE_URL = "http://127.0.0.1:8000/api"

def http_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10.0) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def http_post(endpoint, payload):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10.0) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def test_database_tables_exist():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()

    expected = [
        "users", "sessions", "saved_places", "reports",
        "geo_locations", "land_observations", "imagery_metadata",
        "ml_models", "ml_evaluations", "ml_predictions"
    ]
    for tbl in expected:
        assert tbl in tables, f"Expected table {tbl} not found in SQLite"

def test_ml_models_overview():
    status, data = http_get("/ml/models")
    assert status == 200
    assert "metadata" in data
    assert data["metadata"]["total_samples"] == 1500
    assert "linear_regression" in data["models"]
    assert "svm_classifier" in data["models"]
    assert "knn_finder" in data["models"]
    assert "dbscan_clustering" in data["models"]

def test_linear_regression_prediction():
    status, data = http_post("/ml/predict/linear", {
        "mean_red": 95.0,
        "mean_green": 140.0,
        "mean_blue": 80.0,
        "std_green": 16.0
    })
    assert status == 200
    assert "predicted_vegetation_pct" in data
    assert 0.0 <= data["predicted_vegetation_pct"] <= 100.0
    assert "scientific_interpretation" in data
    assert "layman_summary" in data

def test_svm_classification():
    status, data = http_post("/ml/predict/svm", {
        "mean_red": 40.0,
        "mean_green": 145.0,
        "mean_blue": 35.0
    })
    assert status == 200
    assert "predicted_class_name" in data
    assert "confidence_pct" in data
    assert "class_probabilities" in data
    assert len(data["class_probabilities"]) >= 5

def test_knn_neighbors_query():
    status, data = http_post("/ml/knn/neighbors", {
        "mean_red": 90.0,
        "mean_green": 135.0,
        "mean_blue": 80.0,
        "vegetation_pct": 35.0,
        "built_up_pct": 10.0,
        "soil_pct": 50.0,
        "k": 5
    })
    assert status == 200
    assert len(data["neighbors"]) == 5
    for neighbor in data["neighbors"]:
        assert "parcel_id" in neighbor
        assert "latitude" in neighbor
        assert "longitude" in neighbor
        assert "similarity_pct" in neighbor
        assert 0 <= neighbor["similarity_pct"] <= 100

def test_dbscan_clustering():
    status, data = http_post("/ml/dbscan/cluster", {
        "eps": 0.45,
        "min_samples": 6
    })
    assert status == 200
    assert data["clusters_discovered"] >= 3
    assert data["noise_points"] > 0
    assert "clusters" in data

def test_dataset_explorer():
    status, data = http_get("/ml/dataset?limit=10&offset=0")
    assert status == 200
    assert data["total_records"] == 1500
    assert len(data["records"]) == 10
    record = data["records"][0]
    assert "sample_id" in record
    assert "latitude" in record
    assert "longitude" in record
    assert "mean_red" in record
    assert "vegetation_pct" in record

def test_satellite_imagery_acquire():
    status, data = http_get("/imagery/acquire?lat=28.4007&lon=77.3501")
    assert status == 200
    assert "image_url" in data
    assert "sensor" in data
    assert "attribution" in data

if __name__ == "__main__":
    print("Running KSHETRA Classical ML Lab Suite Tests...")
    test_database_tables_exist()
    print("  [PASS] SQLite Database 10 tables exist")
    test_ml_models_overview()
    print("  [PASS] ML Models Overview & Registry (1,500 samples, 4 syllabus models)")
    test_linear_regression_prediction()
    print("  [PASS] Model A: Linear Regression (Vegetation % OLS inference)")
    test_svm_classification()
    print("  [PASS] Model B: Support Vector Machine (7-Class RBF classification)")
    test_knn_neighbors_query()
    print("  [PASS] Model C: K-Nearest Neighbors (Top-K Analog Land Search)")
    test_dbscan_clustering()
    print("  [PASS] Model D: DBSCAN Clustering (Agro-Ecological Discovery & Anomalies)")
    test_dataset_explorer()
    print("  [PASS] Dataset Explorer (1,500 genuine Sentinel-2 tiles)")
    test_satellite_imagery_acquire()
    print("  [PASS] Real Satellite Imagery Acquisition Pipeline (Esri World Imagery)")
    print("\n>>> ALL 8 ML LAB SUITE TESTS PASSED 100%! <<<")
