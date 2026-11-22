"""
Land Shield AI — Comprehensive End-to-End Reliability Test Suite.

Audits and verifies:
1. Health & system telemetry endpoint (/api/health)
2. Sample listing and manifest verification (/api/predict/samples)
3. Inference on all 5 preloaded demo tiles (indices 0, 10, 50, 100, 200)
4. GPU acceleration & CUDA inference verification
5. Land cover metrics, spectral proxies, and 7-class area calculation
6. Custom image upload handling & auto-resampling
7. Invalid sample index error handling (404)
8. Corrupted/invalid file upload error handling (400)
9. Model metrics and training history retrieval (/api/predict/metrics)
10. Frontend asset serving and HTML integrity
"""

import io
import json
import os
import sys
import time
from pathlib import Path
from PIL import Image
from fastapi import HTTPException, UploadFile

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import FRONTEND_DIR, MODEL_CHECKPOINT_PATH, SAMPLES_DIR
from backend.routes.health import health_check
from backend.routes.predict import (
    get_model_metrics,
    get_predictor,
    list_available_samples,
    predict_sample_by_index,
    predict_uploaded_image,
)


def run_tests():
    print("=" * 75)
    print("  LAND SHIELD AI — END-TO-END RELIABILITY AUDIT")
    print("=" * 75)

    passed = 0
    total = 0

    def assert_test(name: str, condition: bool, details: str = ""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name} {f'({details})' if details else ''}")
        else:
            print(f"  [FAIL] {name} - FAILED: {details}")

    # 1. System Health Telemetry Test
    print("\n--- 1. System Health Telemetry ---")
    health = health_check()
    assert_test("Health Status is online", health.status == "online")
    assert_test("Project Name is LAND SHIELD AI", health.project_name == "Land Shield AI")
    assert_test("Model Architecture", health.model_architecture == "SatelliteUNet")
    assert_test("Validation mIoU >= 0.48", health.validation_miou >= 0.48, f"val_miou={health.validation_miou:.4f}")
    assert_test("Validation Accuracy >= 79%", health.validation_accuracy >= 0.79, f"acc={health.validation_accuracy:.2%}")
    assert_test("CUDA Hardware Acceleration", health.cuda_available and health.device == "cuda", f"device={health.device}, gpu={health.gpu_name}")

    # 2. Model Metrics & History Test
    print("\n--- 2. Model Metrics & Training Progression ---")
    metrics = get_model_metrics()
    assert_test("Best mIoU in metrics matches", metrics.best_val_miou >= 0.48)
    assert_test("Epoch history is complete", len(metrics.history) == 25, f"total_epochs={len(metrics.history)}")
    assert_test("Per-class IoU contains 7 classes", len(metrics.per_class_iou) == 7)

    # 3. Sample Manifest & Thumbnail Verification
    print("\n--- 3. Sample Listing & Manifest ---")
    samples = list_available_samples()
    assert_test("5 Preloaded demo samples found", len(samples) == 5, f"count={len(samples)}")
    expected_indices = [0, 10, 50, 100, 200]
    found_indices = [s.index for s in samples]
    assert_test("Sample indices match [0, 10, 50, 100, 200]", found_indices == expected_indices)
    
    all_thumbs = all(s.thumbnail_b64 is not None and s.thumbnail_b64.startswith("data:image/png;base64,") for s in samples)
    assert_test("All samples have valid base64 thumbnails", all_thumbs)

    all_coords = all(s.latitude is not None and s.longitude is not None and s.location_verified for s in samples)
    assert_test("All samples have verified WGS84 geographic coordinates", all_coords)

    # 4. Neural Network Inference across All 5 Demo Samples
    print("\n--- 4. Live CUDA Inference on Demo Samples ---")
    predictor = get_predictor()
    for s in samples:
        t0 = time.perf_counter()
        res = predict_sample_by_index(s.index)
        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000

        valid_lat_lon = (res.latitude is not None) and (res.longitude is not None)
        valid_breakdown = len(res.class_breakdown) == 7
        pct_sum = sum(stat.percentage for stat in res.class_breakdown.values())
        valid_pct = abs(pct_sum - 100.0) < 0.2
        valid_images = all(k in res.images for k in ["original", "colorized_mask", "side_by_side", "legend"])
        
        assert_test(
            f"Sample {s.index:03d} ({s.description[:25]}...)",
            valid_lat_lon and valid_breakdown and valid_pct and valid_images and res.device == "cuda",
            f"latency={latency_ms:.1f}ms, dominant={res.dominant_class} ({res.dominant_percentage:.1f}%), conf={res.mean_confidence_pct:.1f}%"
        )

    # 5. High-Level Aggregated Proxies & Area Calculation
    print("\n--- 5. Spectral Proxies & Spatial Telemetry ---")
    sample_res = predict_sample_by_index(0)
    assert_test("Total area is 40.96 hectares", sample_res.total_area_hectares == 40.96)
    assert_test("Total pixel count is 4096 (64x64)", sample_res.total_pixels == 4096)
    assert_test("Spatial resolution is 10.0m GSD", sample_res.spatial_resolution_meters == 10.0)
    assert_test("Mean confidence > 50%", sample_res.mean_confidence_pct > 50.0, f"conf={sample_res.mean_confidence_pct:.2f}%")
    assert_test("Vegetation proxy computed", sample_res.vegetation_coverage_pct >= 0.0)
    assert_test("Built-up proxy computed", sample_res.built_up_coverage_pct >= 0.0)

    # 6. Custom Image Upload & Auto-Resampling
    print("\n--- 6. Custom Image Upload & Preprocessing ---")
    # Test valid 64x64 synthetic image
    synthetic_img = Image.new("RGB", (64, 64), color=(60, 140, 60))
    buf = io.BytesIO()
    synthetic_img.save(buf, format="PNG")
    buf.seek(0)
    upload_file = UploadFile(filename="custom_64x64.png", file=buf)
    
    upload_res = predict_uploaded_image(upload_file, allow_resize=True)
    assert_test("Valid 64x64 custom upload succeeds", upload_res.total_pixels == 4096)
    assert_test("Unreferenced upload marks location_verified=False", not upload_res.location_verified)

    # Test auto-resampling from arbitrary resolution (e.g. 256x256)
    large_img = Image.new("RGB", (256, 256), color=(120, 80, 50))
    buf_large = io.BytesIO()
    large_img.save(buf_large, format="JPEG")
    buf_large.seek(0)
    upload_file_large = UploadFile(filename="custom_256x256.jpg", file=buf_large)

    upload_res_large = predict_uploaded_image(upload_file_large, allow_resize=True)
    assert_test("Custom 256x256 image auto-resamples to 64x64", upload_res_large.total_pixels == 4096)

    # 7. Robust Error Handling (404 on Missing Sample & 400 on Corrupted File)
    print("\n--- 7. Error Handling & Edge Cases ---")
    # Missing sample index
    try:
        predict_sample_by_index(99999)
        assert_test("Invalid sample index returns 404", False, "No exception raised")
    except HTTPException as e:
        assert_test("Invalid sample index returns 404", e.status_code == 404, f"status={e.status_code}")

    # Corrupted / invalid file upload
    corrupt_buf = io.BytesIO(b"Not an image file - random text content")
    upload_corrupt = UploadFile(filename="invalid.txt", file=corrupt_buf)
    try:
        predict_uploaded_image(upload_corrupt, allow_resize=True)
        assert_test("Corrupt file returns 400", False, "No exception raised")
    except HTTPException as e:
        assert_test("Corrupt file returns 400", e.status_code == 400, f"status={e.status_code}")

    # 8. Frontend Assets & UI Verification
    print("\n--- 8. Frontend Dashboard Integrity ---")
    index_html = FRONTEND_DIR / "index.html"
    assert_test("index.html exists", index_html.is_file())
    html_content = index_html.read_text(encoding="utf-8")
    assert_test("Branded as Land Shield AI", "Land Shield AI" in html_content)
    assert_test("Zero old names in HTML", "pand shield" not in html_content.lower())
    assert_test("MapLibre GL library included", "maplibre-gl" in html_content)
    assert_test("Broken CARTO tiles removed (no cartocdn.com)", "cartocdn.com" not in html_content)
    assert_test("Keyless OpenStreetMap source present", "tile.openstreetmap.org" in html_content)
    assert_test("Keyless Esri Satellite source present", "World_Imagery/MapServer" in html_content)
    assert_test("Keyless Esri Dark Canvas source present", "World_Dark_Gray_Base/MapServer" in html_content)
    assert_test("Map layer toggle buttons present", all(b in html_content for b in ["btnLayerDark", "btnLayerSat", "btnLayerOSM"]))
    assert_test("Tile attributions properly configured", "OpenStreetMap" in html_content and "Esri" in html_content)
    assert_test("Blend slider control present", 'id="opacitySlider"' in html_content)
    assert_test("Report modal present", 'id="reportModal"' in html_content)
    assert_test("Audit notice on missing data present", "Not available in current dataset" in html_content)

    print("\n" + "=" * 75)
    print(f"  RESULTS: {passed}/{total} TESTS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 75)

    if passed == total:
        print("\n  >> ALL END-TO-END AUDIT CHECKS COMPLETED SUCCESSFULLY. SYSTEM IS PRODUCTION READY! <<\n")
    else:
        print("\n  >> WARNING: SOME CHECKS FAILED. PLEASE REVIEW LOGS. <<\n")


if __name__ == "__main__":
    run_tests()
