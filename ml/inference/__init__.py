"""
Inference Subsystem for Land Shield AI.

Provides production-ready inference and visualization pipelines
for satellite land-cover segmentation using SatelliteUNet.
"""

from ml.inference.predictor import LandCoverPredictor, PredictionResult

__all__ = ["LandCoverPredictor", "PredictionResult"]
