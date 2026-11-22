"""
Point Dataset Harmonizer for Pand Shield AI.

Harmonizes multi-temporal ground truth point datasets (2016 vs 2024)
preserving full 64-bit coordinate precision without rounding.
"""

import json
import logging
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

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
    """Calculates geodesic distance between two points in meters using Haversine formula."""
    r = 6371000.0  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2.0) ** 2
    )
    return r * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


@dataclass
class HarmonizedRecord:
    point_id: str
    longitude: float  # Reference longitude (2024)
    latitude: float  # Reference latitude (2024)
    longitude_2016: float  # Original raw unrounded 2016 longitude
    latitude_2016: float  # Original raw unrounded 2016 latitude
    longitude_2024: float  # Original raw unrounded 2024 longitude
    latitude_2024: float  # Original raw unrounded 2024 latitude
    spatial_drift_meters: float
    match_type: str  # EXACT_COORDINATE_MATCH or SPATIAL_PROXIMITY_MATCH
    system_index_2016: str
    system_index_2024: str
    landcover_2016: int
    landcover_2024: int
    transition_code: str  # e.g. '0_to_0', '0_to_2', '1_to_1'
    transition_category: str  # e.g. 'STABLE_CLASS_0', 'CONVERTED_0_TO_2'
    is_stable: bool


class PointHarmonizer:
    """
    Standardizes and cross-references multi-year point datasets.
    """

    def __init__(self, proximity_threshold_meters: float = 15.0):
        self.proximity_threshold_meters = proximity_threshold_meters

    def harmonize(
        self,
        path_2016: Union[str, Path],
        path_2024: Union[str, Path],
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Harmonizes 2016 and 2024 training points preserving raw coordinate precision.
        """
        p16 = Path(path_2016)
        p24 = Path(path_2024)

        if not p16.is_file():
            raise FileNotFoundError(f"2016 dataset not found: {p16}")
        if not p24.is_file():
            raise FileNotFoundError(f"2024 dataset not found: {p24}")

        logger.info("Loading raw points from %s and %s", p16.name, p24.name)
        df16 = pd.read_csv(p16)
        df24 = pd.read_csv(p24)

        # Parse GeoJSON coordinates without rounding
        def extract_coords(df: pd.DataFrame) -> List[Tuple[float, float]]:
            coords = []
            for raw in df[".geo"]:
                geom = json.loads(raw)
                c = geom["coordinates"]
                coords.append((float(c[0]), float(c[1])))
            return coords

        df16["_coords"] = extract_coords(df16)
        df24["_coords"] = extract_coords(df24)

        # Build lookup tables keyed by exact (float64, float64) tuples
        dict16 = {row["_coords"]: row for _, row in df16.iterrows()}
        dict24 = {row["_coords"]: row for _, row in df24.iterrows()}

        set16 = set(dict16.keys())
        set24 = set(dict24.keys())

        exact_matches = set16.intersection(set24)
        unmatched16 = set16 - exact_matches
        unmatched24 = set24 - exact_matches

        logger.info(
            "Coordinate matching: %d exact matches, %d unmatched in 2016, %d unmatched in 2024",
            len(exact_matches),
            len(unmatched16),
            len(unmatched24),
        )

        records: List[HarmonizedRecord] = []
        drift_log: List[Dict[str, Any]] = []
        pt_counter = 1

        # 1. Process exact coordinate matches (sorted deterministically by latitude, longitude)
        sorted_exact = sorted(list(exact_matches), key=lambda c: (c[1], c[0]))
        for coord in sorted_exact:
            r16 = dict16[coord]
            r24 = dict24[coord]

            l16 = int(r16["landcover"])
            l24 = int(r24["landcover"])
            is_stable = bool(l16 == l24)

            trans_code = f"{l16}_to_{l24}"
            trans_cat = f"STABLE_CLASS_{l16}" if is_stable else f"CONVERTED_{l16}_TO_{l24}"

            records.append(
                HarmonizedRecord(
                    point_id=f"PT_{pt_counter:04d}",
                    longitude=coord[0],
                    latitude=coord[1],
                    longitude_2016=coord[0],
                    latitude_2016=coord[1],
                    longitude_2024=coord[0],
                    latitude_2024=coord[1],
                    spatial_drift_meters=0.0,
                    match_type="EXACT_COORDINATE_MATCH",
                    system_index_2016=str(r16["system:index"]),
                    system_index_2024=str(r24["system:index"]),
                    landcover_2016=l16,
                    landcover_2024=l24,
                    transition_code=trans_code,
                    transition_category=trans_cat,
                    is_stable=is_stable,
                )
            )
            pt_counter += 1

        # 2. Process spatial proximity pairs for remaining points
        matched_u24: Set[Tuple[float, float]] = set()

        for c16 in sorted(list(unmatched16), key=lambda c: (c[1], c[0])):
            r16 = dict16[c16]
            best_match: Optional[Tuple[float, float]] = None
            best_dist: float = float("inf")

            for c24 in unmatched24:
                if c24 in matched_u24:
                    continue
                dist = haversine_distance_meters(c16[0], c16[1], c24[0], c24[1])
                if dist <= self.proximity_threshold_meters and dist < best_dist:
                    best_dist = dist
                    best_match = c24

            if best_match is not None:
                r24 = dict24[best_match]
                matched_u24.add(best_match)

                l16 = int(r16["landcover"])
                l24 = int(r24["landcover"])
                is_stable = bool(l16 == l24)
                trans_code = f"{l16}_to_{l24}"
                trans_cat = f"STABLE_CLASS_{l16}" if is_stable else f"CONVERTED_{l16}_TO_{l24}"

                records.append(
                    HarmonizedRecord(
                        point_id=f"PT_{pt_counter:04d}",
                        longitude=best_match[0],
                        latitude=best_match[1],
                        longitude_2016=c16[0],
                        latitude_2016=c16[1],
                        longitude_2024=best_match[0],
                        latitude_2024=best_match[1],
                        spatial_drift_meters=round(best_dist, 4),
                        match_type=f"SPATIAL_PROXIMITY_MATCH_{round(best_dist)}M",
                        system_index_2016=str(r16["system:index"]),
                        system_index_2024=str(r24["system:index"]),
                        landcover_2016=l16,
                        landcover_2024=l24,
                        transition_code=trans_code,
                        transition_category=trans_cat,
                        is_stable=is_stable,
                    )
                )
                drift_log.append(
                    {
                        "point_id": f"PT_{pt_counter:04d}",
                        "coords_2016": c16,
                        "coords_2024": best_match,
                        "distance_meters": round(best_dist, 4),
                        "landcover_2016": l16,
                        "landcover_2024": l24,
                        "reason": "Points correspond to identical land feature sampled with slight GPS/pin placement offset.",
                    }
                )
                pt_counter += 1
            else:
                logger.warning("Unmatched 2016 point at %s: No candidate within threshold", c16)

        # 3. Check for any remaining unmatched 2024 points
        remaining_u24 = unmatched24 - matched_u24
        for c24 in remaining_u24:
            logger.warning("Unmatched 2024 point at %s: No candidate within threshold", c24)

        harmonized_df = pd.DataFrame([asdict(r) for r in records])

        summary_metrics = {
            "total_records_2016": len(df16),
            "total_records_2024": len(df24),
            "harmonized_records_count": len(harmonized_df),
            "exact_matches_count": len(exact_matches),
            "proximity_matches_count": len(drift_log),
            "unmatched_records_count": len(unmatched16 - set(dict16.keys()))
            + len(remaining_u24),
            "transition_distribution": harmonized_df["transition_code"].value_counts().to_dict(),
            "stable_records_count": int(harmonized_df["is_stable"].sum()),
            "converted_records_count": int((~harmonized_df["is_stable"]).sum()),
            "drift_records": drift_log,
        }

        return harmonized_df, summary_metrics
