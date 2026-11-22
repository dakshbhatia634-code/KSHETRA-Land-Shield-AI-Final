"""
Prediction Routes for Land Shield AI.
"""

import base64
from datetime import datetime, timezone
from io import BytesIO
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from backend.config import (
    MODEL_CHECKPOINT_PATH,
    PIXEL_AREA_HECTARES,
    PREDICTIONS_DIR,
    SAMPLES_DIR,
)
from backend.schemas import ClassStat, ModelMetricsResponse, PredictionResponse, SampleItem
from ml.inference.predictor import LandCoverPredictor, PredictionResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["prediction"])

# Singleton predictor instance
_predictor: Optional[LandCoverPredictor] = None


def get_predictor() -> LandCoverPredictor:
    """Returns or lazily initializes the singleton LandCoverPredictor."""
    global _predictor
    if _predictor is None:
        logger.info("Initializing singleton LandCoverPredictor for API...")
        _predictor = LandCoverPredictor(checkpoint_path=MODEL_CHECKPOINT_PATH)
    return _predictor


def pil_to_base64_data_uri(img: Image.Image, format: str = "PNG") -> str:
    """Converts a PIL Image to a Base64-encoded Data URI string."""
    buf = BytesIO()
    img.save(buf, format=format)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{encoded}"


def rgb_to_hex(rgb: List[int]) -> str:
    """Converts [r, g, b] to '#rrggbb'."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def format_prediction_response(
    res: PredictionResult,
    original_pil: Image.Image,
    geo_meta: Optional[Dict] = None,
    upscale_factor: int = 4,
) -> PredictionResponse:
    """Formats internal PredictionResult into an API-ready PredictionResponse with Base64 images."""
    total_pixels = int(res.predicted_mask.size)
    total_area_ha = round(total_pixels * PIXEL_AREA_HECTARES, 2)

    # Format class breakdown with area, hex colors, and spectral descriptions
    breakdown = {}
    dominant_key = "class_6"
    dominant_count = -1

    for key, stats in res.class_breakdown.items():
        count = stats["pixel_count"]
        if count > dominant_count:
            dominant_count = count
            dominant_key = key

        rgb = stats["color_rgb"]
        breakdown[key] = ClassStat(
            class_id=stats["class_id"],
            class_name=stats["class_name"],
            spectral_description=stats.get("spectral_description", "Spectral Class"),
            pixel_count=count,
            percentage=stats["percentage"],
            area_hectares=round(count * PIXEL_AREA_HECTARES, 2),
            color_hex=rgb_to_hex(rgb),
            color_rgb=rgb,
        )

    dom_stats = breakdown[dominant_key]

    # Calculate aggregated high-level proxies
    veg_pct = round(
        breakdown.get("class_2", ClassStat(class_id=2, class_name="", spectral_description="", pixel_count=0, percentage=0.0, area_hectares=0, color_hex="", color_rgb=[])).percentage +
        breakdown.get("class_3", ClassStat(class_id=3, class_name="", spectral_description="", pixel_count=0, percentage=0.0, area_hectares=0, color_hex="", color_rgb=[])).percentage +
        breakdown.get("class_4", ClassStat(class_id=4, class_name="", spectral_description="", pixel_count=0, percentage=0.0, area_hectares=0, color_hex="", color_rgb=[])).percentage,
        2
    )
    water_pct = breakdown.get("class_1", ClassStat(class_id=1, class_name="", spectral_description="", pixel_count=0, percentage=0.0, area_hectares=0, color_hex="", color_rgb=[])).percentage
    built_pct = breakdown.get("class_6", ClassStat(class_id=6, class_name="", spectral_description="", pixel_count=0, percentage=0.0, area_hectares=0, color_hex="", color_rgb=[])).percentage
    soil_pct = breakdown.get("class_5", ClassStat(class_id=5, class_name="", spectral_description="", pixel_count=0, percentage=0.0, area_hectares=0, color_hex="", color_rgb=[])).percentage

    # Upscale masks for display
    upscale_size = (64 * upscale_factor, 64 * upscale_factor)
    colorized_large = res.colorized_mask.resize(upscale_size, Image.Resampling.NEAREST)
    original_large = original_pil.resize(upscale_size, Image.Resampling.NEAREST)

    images_dict = {
        "original": pil_to_base64_data_uri(original_large),
        "colorized_mask": pil_to_base64_data_uri(colorized_large),
        "side_by_side": pil_to_base64_data_uri(res.side_by_side),
        "legend": pil_to_base64_data_uri(res.legend_image),
    }

    geo = geo_meta or {}

    return PredictionResponse(
        sample_name=res.sample_name,
        inference_time_ms=res.inference_time_ms,
        device=res.device,
        checkpoint_epoch=res.checkpoint_epoch,
        best_val_miou=res.best_val_miou,
        mean_confidence_pct=res.mean_confidence_pct,
        total_pixels=total_pixels,
        total_area_hectares=total_area_ha,
        spatial_resolution_meters=10.0,
        data_source="Sentinel-2 L2A Optical Earth Observation (10m GSD)",
        analysis_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        dominant_class=dom_stats.class_name,
        dominant_percentage=dom_stats.percentage,
        dominant_color_hex=dom_stats.color_hex,
        vegetation_coverage_pct=veg_pct,
        water_moisture_coverage_pct=water_pct,
        built_up_coverage_pct=built_pct,
        bare_soil_coverage_pct=soil_pct,
        latitude=geo.get("latitude"),
        longitude=geo.get("longitude"),
        location_verified=geo.get("location_verified", False),
        coordinate_system=geo.get("coordinate_system"),
        class_breakdown=breakdown,
        images=images_dict,
    )


@router.post("/upload", response_model=PredictionResponse)
def predict_uploaded_image(
    file: UploadFile = File(...),
    allow_resize: bool = True,
):
    """
    Accepts an uploaded satellite image tile and returns live 7-class land-cover segmentation.
    """
    predictor = get_predictor()

    try:
        content = file.file.read()
        pil_img = Image.open(BytesIO(content)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image file: {e}",
        )

    try:
        sample_name = Path(file.filename or "uploaded_tile").stem
        res = predictor.predict(
            image_input=pil_img,
            sample_name=sample_name,
            allow_resize=allow_resize,
        )
        return format_prediction_response(
            res,
            pil_img,
            geo_meta={"location_verified": False, "coordinate_system": "User Upload (Unreferenced)"},
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Inference exception: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")


@router.get("/sample/{index}", response_model=PredictionResponse)
@router.post("/sample/{index}", response_model=PredictionResponse)
def predict_sample_by_index(index: int):
    """
    Executes inference on one of the pre-extracted demo satellite sample tiles.
    """
    predictor = get_predictor()
    sample_file = SAMPLES_DIR / f"sample_tile_{index:05d}.png"

    if not sample_file.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Sample tile index {index} not found. Available samples: [0, 10, 50, 100, 200]",
        )

    # Lookup geo metadata from manifest if available
    geo_meta = None
    manifest_path = SAMPLES_DIR / "sample_manifest.json"
    if manifest_path.is_file():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            for item in manifest:
                if item.get("index") == index:
                    geo_meta = item
                    break
        except Exception:
            pass

    try:
        pil_img = Image.open(sample_file).convert("RGB")
        res = predictor.predict(
            image_input=pil_img,
            sample_name=sample_file.stem,
            allow_resize=False,
        )
        return format_prediction_response(res, pil_img, geo_meta=geo_meta)
    except Exception as e:
        logger.error("Sample inference exception: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")


@router.get("/samples", response_model=List[SampleItem])
def list_available_samples():
    """
    Returns the list of preloaded demo satellite tiles with thumbnails and geographic descriptions.
    """
    manifest_path = SAMPLES_DIR / "sample_manifest.json"
    if not manifest_path.is_file():
        return []

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    results = []
    for item in manifest:
        fpath = Path(item["path"])
        thumb_b64 = None
        if fpath.is_file():
            try:
                img = Image.open(fpath).resize((64, 64), Image.Resampling.NEAREST)
                thumb_b64 = pil_to_base64_data_uri(img)
            except Exception:
                pass

        results.append(
            SampleItem(
                index=item["index"],
                filename=item["filename"],
                sample_id=item["sample_id"],
                description=item["description"],
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                location_verified=item.get("location_verified", False),
                easting=item.get("easting"),
                northing=item.get("northing"),
                coordinate_system=item.get("coordinate_system"),
                thumbnail_b64=thumb_b64,
            )
        )
    return results


@router.get("/metrics", response_model=ModelMetricsResponse)
def get_model_metrics():
    """
    Returns validation mIoU, per-class IoU, accuracy, and full training progression.
    """
    history_path = MODEL_CHECKPOINT_PATH.parent / "training_history.json"
    if not history_path.is_file():
        raise HTTPException(status_code=404, detail="Training history not found.")

    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)

    best_entry = max(history, key=lambda x: x.get("val_metrics", {}).get("mean_iou", 0))
    val_metrics = best_entry.get("val_metrics", {})

    return ModelMetricsResponse(
        architecture="SatelliteUNet (4-level Encoder-Decoder)",
        total_epochs=len(history),
        best_val_miou=val_metrics.get("mean_iou", 0.4839),
        validation_accuracy=val_metrics.get("overall_accuracy", 0.7959),
        per_class_iou=val_metrics.get("per_class_iou", {}),
        history=history,
    )
