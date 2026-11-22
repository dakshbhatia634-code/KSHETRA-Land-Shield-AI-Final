"""
Data Schemas for Land Shield AI Backend API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "online"
    project_name: str = "Land Shield AI"
    tagline: str
    model_architecture: str = "SatelliteUNet"
    checkpoint_epoch: Optional[int] = None
    validation_miou: Optional[float] = None
    validation_accuracy: Optional[float] = None
    device: str
    cuda_available: bool
    gpu_name: Optional[str] = None
    total_classes: int = 7


class ClassStat(BaseModel):
    class_id: int
    class_name: str
    spectral_description: str
    pixel_count: int
    percentage: float
    area_hectares: float
    color_hex: str
    color_rgb: List[int]


class PredictionResponse(BaseModel):
    sample_name: str
    inference_time_ms: float
    device: str
    checkpoint_epoch: Optional[int] = None
    best_val_miou: Optional[float] = None
    mean_confidence_pct: Optional[float] = None
    total_pixels: int = 4096
    total_area_hectares: float = 40.96
    spatial_resolution_meters: float = 10.0
    data_source: str = "Sentinel-2 L2A Optical Earth Observation (10m GSD)"
    analysis_timestamp: str
    dominant_class: str
    dominant_percentage: float
    dominant_color_hex: str
    vegetation_coverage_pct: float
    water_moisture_coverage_pct: float
    built_up_coverage_pct: float
    bare_soil_coverage_pct: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_verified: bool = False
    coordinate_system: Optional[str] = None
    unsupported_indicators: Dict[str, str] = Field(
        default_factory=lambda: {
            "property_ownership": "Not available in current dataset",
            "soil_fertility": "Not available in current dataset",
            "zoning_cadastral": "Not available in current dataset",
        }
    )
    class_breakdown: Dict[str, ClassStat]
    images: Dict[str, str] = Field(
        default_factory=dict,
        description="Base64 PNG data URLs for visual rendering"
    )


class SampleItem(BaseModel):
    index: int
    filename: str
    sample_id: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_verified: bool = False
    easting: Optional[float] = None
    northing: Optional[float] = None
    coordinate_system: Optional[str] = None
    thumbnail_b64: Optional[str] = None


class ModelMetricsResponse(BaseModel):
    architecture: str
    total_epochs: int
    best_val_miou: float
    validation_accuracy: float
    per_class_iou: Dict[str, float]
    history: List[Dict[str, Any]]


class GeoSearchResult(BaseModel):
    display_name: str
    name: str
    latitude: float
    longitude: float
    type: str = "locality"
    state: Optional[str] = None
    district: Optional[str] = None
    boundingbox: Optional[List[float]] = None
    data_state: str = "Verified"
    source: str = "OpenStreetMap / Nominatim"


class EnvironmentalTelemetry(BaseModel):
    latitude: float
    longitude: float
    resolved_place_name: Optional[str] = None
    temperature_c: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    precipitation_mm: Optional[float] = None
    weather_condition: Optional[str] = None
    wind_speed_kmh: Optional[float] = None
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    weather_data_state: str = "Verified"
    elevation_data_state: str = "Estimated"
    soil_data_state: str = "Unavailable"
    cadastral_data_state: str = "Unavailable"
    data_states: Dict[str, str] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)

