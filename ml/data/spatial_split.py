"""
Spatial Grouping & Train/Val Split Engine for Pand Shield AI.

Partitions satellite tiles into spatially isolated geographic blocks (e.g., 20 km x 20 km)
to eliminate spatial autocorrelation and prevent geographic data leakage between train and val.
"""

import json
import logging
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass
class TileSpatialRecord:
    global_index: int
    sample_id: str
    easting: float
    northing: float
    block_id: str
    split: str  # 'train' or 'val'


class SpatialSplitEngine:
    """
    Creates and validates spatially grouped train/val splits.
    """

    def __init__(
        self,
        parquet_path: Union[str, Path] = "data/raw/train-00000-of-00007.parquet",
        block_size_km: float = 20.0,
        val_ratio: float = 0.20,
        random_seed: int = 42,
    ):
        self.parquet_path = Path(parquet_path)
        self.block_size_meters = block_size_km * 1000.0
        self.val_ratio = val_ratio
        self.random_seed = random_seed

    def extract_tile_coordinates(self) -> List[Tuple[int, str, float, float]]:
        """
        Extracts UTM easting and northing for all tiles from Parquet metadata strips.
        Returns: list of (global_index, sample_id, easting, northing)
        """
        logger.info("Extracting spatial tiepoints from %s...", self.parquet_path.name)
        pfile = pq.ParquetFile(str(self.parquet_path))
        results = []
        global_idx = 0

        for rg in range(pfile.num_row_groups):
            df_rg = pfile.read_row_group(rg, columns=["mask.bytes", "rgb.path"]).to_pandas()
            for _, row in df_rg.iterrows():
                mb = row["mask"]["bytes"]
                sample_id = row["rgb"]["path"]
                tp = struct.unpack("<6d", mb[238 : 238 + 48])
                easting = tp[3]
                northing = tp[4]
                results.append((global_idx, sample_id, easting, northing))
                global_idx += 1

        logger.info("Extracted %d tile coordinates.", len(results))
        return results

    def compute_spatial_split(
        self,
        cache_path: Optional[Union[str, Path]] = "data/processed/splits/spatial_train_val_split.json",
        force_recompute: bool = False,
    ) -> Tuple[List[int], List[int], Dict[str, Any]]:
        """
        Partitions tiles into spatially grouped train/val sets and returns (train_indices, val_indices, metadata).
        """
        if cache_path:
            cpath = Path(cache_path)
            if cpath.is_file() and not force_recompute:
                logger.info("Loading cached spatial split from %s", cpath.name)
                with open(cpath, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                return (
                    cached["train_indices"],
                    cached["val_indices"],
                    cached["metadata"],
                )

        tiles = self.extract_tile_coordinates()
        min_x = min(t[2] for t in tiles)
        min_y = min(t[3] for t in tiles)

        # Map each tile to a spatial grid block ID
        blocks: Dict[str, List[int]] = {}
        tile_to_block: Dict[int, str] = {}

        for idx, sid, easting, northing in tiles:
            grid_x = int((easting - min_x) // self.block_size_meters)
            grid_y = int((northing - min_y) // self.block_size_meters)
            block_id = f"block_{grid_x:02d}_{grid_y:02d}"

            if block_id not in blocks:
                blocks[block_id] = []
            blocks[block_id].append(idx)
            tile_to_block[idx] = block_id

        logger.info(
            "Discretized spatial extent into %d contiguous blocks of size %.1f km.",
            len(blocks),
            self.block_size_meters / 1000.0,
        )

        # Deterministically partition blocks
        rng = np.random.RandomState(self.random_seed)
        block_keys = sorted(list(blocks.keys()))
        rng.shuffle(block_keys)

        total_tiles = len(tiles)
        target_val_count = int(total_tiles * self.val_ratio)

        val_blocks: Set[str] = set()
        val_indices: List[int] = []
        train_blocks: Set[str] = set()
        train_indices: List[int] = []

        curr_val_count = 0
        for b_id in block_keys:
            b_indices = blocks[b_id]
            if curr_val_count + len(b_indices) <= target_val_count or curr_val_count == 0:
                val_blocks.add(b_id)
                val_indices.extend(b_indices)
                curr_val_count += len(b_indices)
            else:
                train_blocks.add(b_id)
                train_indices.extend(b_indices)

        # Sort indices deterministically
        train_indices.sort()
        val_indices.sort()

        logger.info(
            "Spatial split complete: %d train tiles (%d blocks) | %d val tiles (%d blocks)",
            len(train_indices),
            len(train_blocks),
            len(val_indices),
            len(val_blocks),
        )

        # Verify zero block overlap (strict leak prevention)
        overlap = train_blocks.intersection(val_blocks)
        if overlap:
            raise RuntimeError(f"Critical error: Spatial block overlap detected: {overlap}")

        metadata = {
            "total_tiles": total_tiles,
            "block_size_km": self.block_size_meters / 1000.0,
            "total_spatial_blocks": len(blocks),
            "train_blocks_count": len(train_blocks),
            "val_blocks_count": len(val_blocks),
            "train_tiles_count": len(train_indices),
            "val_tiles_count": len(val_indices),
            "train_percentage": round((len(train_indices) / total_tiles) * 100, 2),
            "val_percentage": round((len(val_indices) / total_tiles) * 100, 2),
            "leakage_prevention": "STRICT_SPATIAL_BLOCK_ISOLATION",
            "random_seed": self.random_seed,
        }

        if cache_path:
            cpath = Path(cache_path)
            cpath.parent.mkdir(parents=True, exist_ok=True)
            with open(cpath, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "metadata": metadata,
                        "train_indices": train_indices,
                        "val_indices": val_indices,
                        "train_blocks": sorted(list(train_blocks)),
                        "val_blocks": sorted(list(val_blocks)),
                    },
                    f,
                    indent=2,
                )
            logger.info("Saved spatial split registry to %s", cpath.name)

        return train_indices, val_indices, metadata
