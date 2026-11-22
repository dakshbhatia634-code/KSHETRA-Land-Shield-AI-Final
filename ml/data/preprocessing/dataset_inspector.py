"""
Unified Dataset Inspector for Pand Shield AI.

Provides memory-efficient inspection for both tabular CSV datasets and
binary-encoded Parquet satellite imagery shards.
"""

import json
import logging
import struct
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
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


class DatasetInspector:
    """
    Performs memory-conscious auditing of CSV and Parquet datasets.
    """

    @staticmethod
    def inspect_csv(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Inspects a CSV dataset reporting structure, dtypes, nulls, and coordinates.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"CSV file not found: {path}")

        logger.info("Inspecting CSV: %s", path.name)
        df = pd.read_csv(path)

        nulls = df.isnull().sum().to_dict()
        duplicates = int(df.duplicated().sum())

        # Coordinates & labels
        lons, lats = [], []
        has_geo = ".geo" in df.columns
        if has_geo:
            for g in df[".geo"]:
                try:
                    coords = json.loads(g).get("coordinates", [])
                    if len(coords) >= 2:
                        lons.append(float(coords[0]))
                        lats.append(float(coords[1]))
                except Exception:
                    pass

        label_dist = {}
        if "landcover" in df.columns:
            label_dist = {int(k): int(v) for k, v in df["landcover"].value_counts().items()}

        report: Dict[str, Any] = {
            "file_name": path.name,
            "format": "CSV",
            "file_size_bytes": path.stat().st_size,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_values": nulls,
            "duplicate_rows": duplicates,
            "label_distribution": label_dist,
            "has_coordinates": has_geo and len(lons) > 0,
            "coordinate_bounds": {
                "min_lon": min(lons) if lons else None,
                "max_lon": max(lons) if lons else None,
                "min_lat": min(lats) if lats else None,
                "max_lat": max(lats) if lats else None,
            },
        }
        return report

    @staticmethod
    def inspect_parquet(
        file_path: Union[str, Path], sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Inspects a Parquet satellite dataset using metadata reading and small sampling.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Parquet file not found: {path}")

        logger.info("Inspecting Parquet metadata: %s", path.name)
        pfile = pq.ParquetFile(str(path))
        num_rows = pfile.metadata.num_rows
        num_cols = pfile.metadata.num_columns
        num_rg = pfile.num_row_groups

        # Schema details
        schema_fields = [pfile.schema.names[i] for i in range(len(pfile.schema.names))]

        # Null counts from row group statistics
        null_counts = {}
        for c_idx in range(num_cols):
            col_name = pfile.metadata.row_group(0).column(c_idx).path_in_schema
            total_nulls = 0
            for rg in range(num_rg):
                stats = pfile.metadata.row_group(rg).column(c_idx).statistics
                if stats and stats.has_null_count:
                    total_nulls += stats.null_count
            null_counts[col_name] = total_nulls

        # Sample inspection for image dimensions, mask classes, and coordinates
        first_rg = pfile.read_row_group(0).slice(0, min(sample_size, num_rows))
        df_sample = first_rg.to_pandas()

        image_dims = set()
        mask_dims = set()
        unique_mask_labels = set()
        tiepoints = []
        crs_list = set()

        for _, row in df_sample.iterrows():
            rgb_b = row["rgb"]["bytes"]
            mask_b = row["mask"]["bytes"]

            if rgb_b:
                img = decode_png_rgb(rgb_b)
                image_dims.add(img.shape)

            if mask_b:
                mask, meta = decode_geotiff_mask(mask_b)
                mask_dims.add(mask.shape)
                unique_mask_labels.update(np.unique(mask).tolist())
                if "tiepoint" in meta:
                    tiepoints.append(meta["tiepoint"])
                if "crs_ascii" in meta:
                    crs_list.add(meta["crs_ascii"])

        report: Dict[str, Any] = {
            "file_name": path.name,
            "format": "Apache Parquet",
            "file_size_bytes": path.stat().st_size,
            "rows": num_rows,
            "columns": num_cols,
            "row_groups": num_rg,
            "schema_fields": schema_fields,
            "null_values": null_counts,
            "sample_tested": len(df_sample),
            "image_dimensions": [list(d) for d in image_dims],
            "mask_dimensions": [list(d) for d in mask_dims],
            "unique_mask_labels": sorted(list(unique_mask_labels)),
            "detected_crs": list(crs_list),
            "sample_tiepoint_count": len(tiepoints),
        }
        return report


def main() -> None:
    """CLI runner to execute dataset inspection and display JSON output."""
    raw_dir = Path("data/raw")
    inspector = DatasetInspector()

    for csv_file in raw_dir.glob("*.csv"):
        print("\n" + "=" * 60)
        print(f"REPORT FOR: {csv_file.name}")
        print("=" * 60)
        rep = inspector.inspect_csv(csv_file)
        print(json.dumps(rep, indent=2))

    for pq_file in raw_dir.glob("*.parquet"):
        print("\n" + "=" * 60)
        print(f"REPORT FOR: {pq_file.name}")
        print("=" * 60)
        rep = inspector.inspect_parquet(pq_file, sample_size=50)
        print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
