"""
Parquet Dataset Validator & Label Verification for Pand Shield AI.

Performs memory-conscious streaming validation of satellite image-mask pairs
and verifies mask class statistics without inventing class meanings.
"""

import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pyarrow.parquet as pq

from ml.data.loaders.parquet_loader import decode_geotiff_mask, decode_png_rgb

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ParquetDatasetValidator:
    """
    Validates integrity, dimensions, and label statistics of the Parquet satellite dataset.
    """

    def __init__(self, parquet_path: Union[str, Path]):
        self.parquet_path = Path(parquet_path)
        if not self.parquet_path.is_file():
            raise FileNotFoundError(f"Parquet file not found: {self.parquet_path}")
        self._pfile = pq.ParquetFile(str(self.parquet_path))

    def audit_and_verify_labels(
        self, sample_size: int = 500
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Conducts metadata audit and samples mask pixels to produce label documentation.
        """
        logger.info(
            "Auditing Parquet dataset: %s (%d rows)",
            self.parquet_path.name,
            self._pfile.metadata.num_rows,
        )

        num_rows = self._pfile.metadata.num_rows
        num_cols = self._pfile.metadata.num_columns
        num_rg = self._pfile.num_row_groups

        # Column null check across all row group statistics
        null_stats = {}
        for c_idx in range(num_cols):
            col_name = self._pfile.metadata.row_group(0).column(c_idx).path_in_schema
            total_nulls = 0
            for rg in range(num_rg):
                stats = self._pfile.metadata.row_group(rg).column(c_idx).statistics
                if stats and stats.has_null_count:
                    total_nulls += stats.null_count
            null_stats[col_name] = total_nulls

        # Sample row groups for dimension verification and pixel frequency
        pixel_counter = Counter()
        image_shapes = set()
        mask_shapes = set()
        crs_detected = set()
        scales_detected = set()
        samples_audited = 0

        # Uniformly distribute sample across row groups
        per_rg_sample = max(1, sample_size // num_rg)

        for rg_idx in range(num_rg):
            rg_table = self._pfile.read_row_group(rg_idx).slice(0, per_rg_sample)
            df_chunk = rg_table.to_pandas()

            for _, row in df_chunk.iterrows():
                rgb_b = row["rgb"]["bytes"]
                mask_b = row["mask"]["bytes"]

                if rgb_b:
                    img = decode_png_rgb(rgb_b)
                    image_shapes.add(img.shape)

                if mask_b:
                    mask, meta = decode_geotiff_mask(mask_b)
                    mask_shapes.add(mask.shape)
                    pixel_counter.update(mask.flatten().tolist())

                    if "crs_ascii" in meta:
                        crs_detected.add(meta["crs_ascii"])
                    if "pixel_scale" in meta:
                        scales_detected.add(meta["pixel_scale"])

                samples_audited += 1

        total_pixels = sum(pixel_counter.values())

        # Construct strictly factual label documentation (no invented names)
        label_docs = {
            "status": "NUMERIC_CLASSES_VERIFIED_SEMANTIC_NAMES_UNVERIFIED",
            "policy": "Strict zero-fabrication: Class semantics are reported as integer IDs until verified via ground truth calibration.",
            "total_sampled_pixels": total_pixels,
            "samples_audited_count": samples_audited,
            "classes": {},
        }

        for class_id in sorted(pixel_counter.keys()):
            count = pixel_counter[class_id]
            pct = round((count / total_pixels) * 100, 3) if total_pixels > 0 else 0.0
            label_docs["classes"][str(class_id)] = {
                "class_id": int(class_id),
                "verified_pixel_count": count,
                "frequency_percentage": pct,
                "verified_semantic_name": None,
                "status": "AWAITING_GROUND_TRUTH_CALIBRATION",
            }

        audit_summary = {
            "file_name": self.parquet_path.name,
            "file_size_bytes": self.parquet_path.stat().st_size,
            "total_records": num_rows,
            "row_groups_count": num_rg,
            "columns_count": num_cols,
            "null_counts": null_stats,
            "verified_image_shapes": [list(s) for s in image_shapes],
            "verified_mask_shapes": [list(s) for s in mask_shapes],
            "coordinate_reference_system": list(crs_detected),
            "pixel_scale_meters": [list(s) for s in scales_detected],
            "unique_mask_classes": sorted(list(pixel_counter.keys())),
        }

        return audit_summary, label_docs
