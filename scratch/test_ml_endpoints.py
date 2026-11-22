"""
Direct HTTP test for KSHETRA Classical ML Suite and Imagery Endpoints.
Uses urllib.request (zero external dependencies).
"""

import json
import urllib.request

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

def test_ml_suite():
    print("Testing GET /ml/models...")
    status, data = http_get("/ml/models")
    assert status == 200, f"Expected 200, got {status}"
    assert "linear_regression" in data["models"]
    assert "svm_classifier" in data["models"]
    assert "knn_finder" in data["models"]
    assert "dbscan_clustering" in data["models"]
    print("  Models overview verified: all 4 models present.")

    print("Testing POST /ml/predict/linear...")
    status, lin_res = http_post("/ml/predict/linear", {
        "mean_red": 95.0,
        "mean_green": 140.0,
        "mean_blue": 80.0
    })
    assert status == 200
    print("  Linear Regression result:", lin_res["predicted_vegetation_pct"], "% -", lin_res["scientific_interpretation"])
    assert 0 <= lin_res["predicted_vegetation_pct"] <= 100

    print("Testing POST /ml/predict/svm...")
    status, svm_res = http_post("/ml/predict/svm", {
        "mean_red": 70.0,
        "mean_green": 155.0,
        "mean_blue": 65.0
    })
    assert status == 200
    print("  SVM result:", svm_res["predicted_class_name"], f"({svm_res['confidence_pct']}%)")
    assert "class_probabilities" in svm_res

    print("Testing POST /ml/knn/neighbors...")
    status, knn_res = http_post("/ml/knn/neighbors", {
        "mean_red": 90.0,
        "mean_green": 130.0,
        "mean_blue": 85.0,
        "vegetation_pct": 45.0,
        "built_up_pct": 5.0,
        "soil_pct": 30.0,
        "k": 5
    })
    assert status == 200
    print(f"  KNN result: found {len(knn_res['neighbors'])} neighbors.")
    assert len(knn_res["neighbors"]) == 5
    assert knn_res["neighbors"][0]["similarity_pct"] > 0

    print("Testing POST /ml/dbscan/cluster...")
    status, db_res = http_post("/ml/dbscan/cluster", {
        "eps": 0.45,
        "min_samples": 6
    })
    assert status == 200
    print(f"  DBSCAN result: {db_res['clusters_discovered']} clusters, {db_res['noise_points']} noise points.")
    assert db_res["clusters_discovered"] > 0

    print("Testing GET /ml/dataset?limit=5...")
    status, ds_res = http_get("/ml/dataset?limit=5")
    assert status == 200
    assert len(ds_res["records"]) == 5
    print(f"  Dataset records returned: {len(ds_res['records'])} of {ds_res['total_records']}")

    print("Testing GET /imagery/acquire...")
    status, img_res = http_get("/imagery/acquire?lat=28.4007&lon=77.3501")
    assert status == 200
    print("  Imagery acquire result:", img_res["sensor"], img_res["image_url"])

    print("Testing GET /imagery/metadata...")
    status, meta_res = http_get("/imagery/metadata")
    assert status == 200
    print(f"  Imagery metadata entries: {len(meta_res)}")

    print("\n>>> ALL ML & IMAGERY SUITE HTTP TESTS PASSED 100%! <<<")

if __name__ == "__main__":
    test_ml_suite()
