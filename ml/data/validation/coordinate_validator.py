"""
Geospatial Coordinate Validator for Pand Shield AI.

Performs strict, read-only validation of CSV coordinate datasets
without altering raw files or relying on corrupted index fields.
"""

import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def haversine_distance_meters(
    lon1: float, lat1: float, lon2: float, lat2: float
) -> float:
    """
    Calculates great-circle distance between two WGS84 points in meters.
    """
    radius = 6371000.0  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return radius * c


@dataclass
class CoordinateRecord:
    row_index: int
    system_index: str
    landcover: int
    longitude: float
    latitude: float
    raw_geo: str


@dataclass
class DatasetValidationSummary:
    file_name: str
    total_rows: int
    valid_coords_count: int
    invalid_coords_count: int
    duplicate_coords_count: int
    longitude_range: Tuple[float, float]
    latitude_range: Tuple[float, float]
    is_within_india_bounds: bool
    label_distribution: Dict[int, int]


@dataclass
class CrossDatasetComparison:
    dataset1_name: str
    dataset2_name: str
    dataset1_points: int
    dataset2_points: int
    exact_match_count: int
    unmatched_d1_count: int
    unmatched_d2_count: int
    near_matches_within_10m: List[Dict[str, Any]] = field(default_factory=list)


class CoordinateValidator:
    """
    Validates CSV coordinate datasets and performs coordinate-based cross comparisons.
    """

    # Approximate bounding box for India (including territorial waters and islands)
    INDIA_LON_RANGE = (68.0, 98.0)
    INDIA_LAT_RANGE = (6.0, 38.0)

    def __init__(self, decimal_precision: int = 6):
        self.decimal_precision = decimal_precision

    def parse_and_validate_file(
        self, csv_path: Union[str, Path]
    ) -> Tuple[List[CoordinateRecord], DatasetValidationSummary]:
        """
        Parses a CSV file containing `.geo` GeoJSON points and performs integrity validation.
        """
        path = Path(csv_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        logger.info("Reading and validating coordinate dataset: %s", path.name)
        df = pd.read_csv(path)

        records: List[CoordinateRecord] = []
        lons: List[float] = []
        lats: List[float] = []
        seen_coords: Set[Tuple[float, float]] = set()
        duplicate_coords_count = 0
        invalid_count = 0

        label_counts = df["landcover"].value_counts().to_dict()

        for idx, row in df.iterrows():
            raw_geo = str(row.get(".geo", ""))
            sys_idx = str(row.get("system:index", ""))
            label = int(row.get("landcover", -1))

            try:
                geom = json.loads(raw_geo)
                coords = geom.get("coordinates", [])
                if len(coords) < 2:
                    raise ValueError("Coordinates array has fewer than 2 elements")

                lon = float(coords[0])
                lat = float(coords[1])

                # Check valid global WGS84 range
                if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
                    invalid_count += 1
                    logger.warning("Row %d has out-of-range coordinates: (%f, %f)", idx, lon, lat)
                    continue

                rounded = (
                    round(lon, self.decimal_precision),
                    round(lat, self.decimal_precision),
                )
                if rounded in seen_coords:
                    duplicate_coords_count += 1
                seen_coords.add(rounded)

                lons.append(lon)
                lats.append(lat)
                records.append(
                    CoordinateRecord(
                        row_index=idx,
                        system_index=sys_idx,
                        landcover=label,
                        longitude=lon,
                        latitude=lat,
                        raw_geo=raw_geo,
                    )
                )

            except Exception as err:
                invalid_count += 1
                logger.error("Row %d parsing failed: %s", idx, err)

        min_lon, max_lon = (min(lons), max(lons)) if lons else (0.0, 0.0)
        min_lat, max_lat = (min(lats), max(lats)) if lats else (0.0, 0.0)

        in_india = bool(
            min_lon >= self.INDIA_LON_RANGE[0]
            and max_lon <= self.INDIA_LON_RANGE[1]
            and min_lat >= self.INDIA_LAT_RANGE[0]
            and max_lat <= self.INDIA_LAT_RANGE[1]
        )

        summary = DatasetValidationSummary(
            file_name=path.name,
            total_rows=len(df),
            valid_coords_count=len(records),
            invalid_coords_count=invalid_count,
            duplicate_coords_count=duplicate_coords_count,
            longitude_range=(min_lon, max_lon),
            latitude_range=(min_lat, max_lat),
            is_within_india_bounds=in_india,
            label_distribution=label_counts,
        )

        return records, summary

    def compare_datasets(
        self,
        records1: List[CoordinateRecord],
        name1: str,
        records2: List[CoordinateRecord],
        name2: str,
        drift_tolerance_meters: float = 10.0,
    ) -> CrossDatasetComparison:
        """
        Cross-validates two coordinate datasets purely based on coordinates (ignoring system:index).
        """
        dict1 = {(round(r.longitude, self.decimal_precision), round(r.latitude, self.decimal_precision)): r for r in records1}
        dict2 = {(round(r.longitude, self.decimal_precision), round(r.latitude, self.decimal_precision)): r for r in records2}

        exact_matches = set(dict1.keys()).intersection(set(dict2.keys()))
        unmatched1_keys = set(dict1.keys()) - exact_matches
        unmatched2_keys = set(dict2.keys()) - exact_matches

        near_matches = []
        # Find close spatial discrepancies (e.g. slight sensor/orthorectification shifts)
        for k1 in list(unmatched1_keys):
            r1 = dict1[k1]
            for k2 in list(unmatched2_keys):
                r2 = dict2[k2]
                dist = haversine_distance_meters(
                    r1.longitude, r1.latitude, r2.longitude, r2.latitude
                )
                if dist <= drift_tolerance_meters:
                    near_matches.append(
                        {
                            "d1_point": (r1.longitude, r1.latitude),
                            "d1_label": r1.landcover,
                            "d2_point": (r2.longitude, r2.latitude),
                            "d2_label": r2.landcover,
                            "distance_meters": round(dist, 2),
                        }
                    )

        return CrossDatasetComparison(
            dataset1_name=name1,
            dataset2_name=name2,
            dataset1_points=len(records1),
            dataset2_points=len(records2),
            exact_match_count=len(exact_matches),
            unmatched_d1_count=len(unmatched1_keys),
            unmatched_d2_count=len(unmatched2_keys),
            near_matches_within_10m=near_matches,
        )
