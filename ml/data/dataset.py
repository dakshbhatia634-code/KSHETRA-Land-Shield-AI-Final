"""
PyTorch Dataset for Satellite Land-Cover Segmentation in Pand Shield AI.

Handles image normalization, class ID validation (1-7 -> 0-6),
and memory-conscious batch loading for PyTorch training and evaluation.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pyarrow.parquet as pq
import torch
from torch.utils.data import Dataset

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

# Standard Sentinel-2 optical RGB normalization constants
RGB_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
RGB_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)


class SatelliteSegmentationDataset(Dataset):
    """
    PyTorch Dataset providing normalized satellite imagery and validated integer masks.
    """

    def __init__(
        self,
        parquet_path: Union[str, Path] = "data/raw/train-00000-of-00007.parquet",
        sample_indices: Optional[List[int]] = None,
        sample_limit: Optional[int] = None,
        cache_in_memory: bool = False,
        normalize: bool = True,
    ):
        self.parquet_path = Path(parquet_path)
        if not self.parquet_path.is_file():
            raise FileNotFoundError(f"Parquet file not found: {self.parquet_path}")

        self._pfile = pq.ParquetFile(str(self.parquet_path))
        self.total_dataset_rows = self._pfile.metadata.num_rows

        if sample_indices is not None:
            self.indices = list(sample_indices)
        else:
            self.indices = list(range(self.total_dataset_rows))

        if sample_limit is not None and sample_limit < len(self.indices):
            self.indices = self.indices[:sample_limit]

        self.normalize = normalize
        self.cache_in_memory = cache_in_memory
        self._memory_cache: Dict[int, Tuple[np.ndarray, np.ndarray, str]] = {}

        # Precompute row-group offsets for fast random row retrieval
        self._rg_offsets: List[int] = [0]
        accum = 0
        for rg_idx in range(self._pfile.num_row_groups):
            accum += self._pfile.metadata.row_group(rg_idx).num_rows
            self._rg_offsets.append(accum)

        logger.info(
            "Initialized SatelliteSegmentationDataset with %d samples (cached=%s)",
            len(self.indices),
            cache_in_memory,
        )

        if self.cache_in_memory:
            self._populate_cache()

    def _get_row_group_and_local_index(self, global_idx: int) -> Tuple[int, int]:
        """Locates the row group index and row offset within that group."""
        for rg_idx in range(len(self._rg_offsets) - 1):
            start = self._rg_offsets[rg_idx]
            end = self._rg_offsets[rg_idx + 1]
            if start <= global_idx < end:
                return rg_idx, global_idx - start
        raise IndexError(f"Global index {global_idx} out of range")

    def _fetch_raw_sample(self, global_idx: int) -> Tuple[np.ndarray, np.ndarray, str]:
        """Fetches raw RGB image, mask, and sample ID for a given global row index."""
        if global_idx in self._memory_cache:
            return self._memory_cache[global_idx]

        rg_idx, local_idx = self._get_row_group_and_local_index(global_idx)
        table = self._pfile.read_row_group(rg_idx).slice(local_idx, 1)
        row = table.to_pandas().iloc[0]

        rgb_bytes = row["rgb"]["bytes"]
        mask_bytes = row["mask"]["bytes"]
        sample_id = row["rgb"]["path"]

        image = decode_png_rgb(rgb_bytes)
        mask, _ = decode_geotiff_mask(mask_bytes)

        # Validate dimensions
        if image.shape != (64, 64, 3):
            raise ValueError(f"Sample {sample_id} image shape mismatch: {image.shape}")
        if mask.shape != (64, 64):
            raise ValueError(f"Sample {sample_id} mask shape mismatch: {mask.shape}")

        return image, mask, sample_id

    def _populate_cache(self) -> None:
        """Preloads requested subset into RAM for ultra-fast training iterations."""
        logger.info("Preloading %d samples into memory cache...", len(self.indices))
        # Batch reading for speed
        idx_set = set(self.indices)
        for rg_idx in range(self._pfile.num_row_groups):
            rg_start = self._rg_offsets[rg_idx]
            rg_end = self._rg_offsets[rg_idx + 1]
            # Check if any indices belong to this row group
            rg_indices = [i for i in self.indices if rg_start <= i < rg_end]
            if not rg_indices:
                continue

            table = self._pfile.read_row_group(rg_idx).to_pandas()
            for global_idx in rg_indices:
                local_idx = global_idx - rg_start
                row = table.iloc[local_idx]
                image = decode_png_rgb(row["rgb"]["bytes"])
                mask, _ = decode_geotiff_mask(row["mask"]["bytes"])
                sample_id = row["rgb"]["path"]
                self._memory_cache[global_idx] = (image, mask, sample_id)

        logger.info("Cached %d samples successfully.", len(self._memory_cache))

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, str]:
        global_idx = self.indices[idx]
        image_np, mask_np, sample_id = self._fetch_raw_sample(global_idx)

        # 1. Image preprocessing: (H, W, 3) uint8 -> (3, H, W) float32 in [0, 1]
        img_tensor = torch.from_numpy(image_np).permute(2, 0, 1).to(torch.float32) / 255.0

        if self.normalize:
            mean = torch.tensor(RGB_MEAN, dtype=torch.float32)
            std = torch.tensor(RGB_STD, dtype=torch.float32)
            img_tensor = (img_tensor - mean) / std

        # 2. Mask validation & conversion: classes 1..7 -> zero-indexed 0..6
        # Any unexpected value is clamped or raised
        mask_clean = mask_np.copy().astype(np.int64)
        if np.any((mask_clean < 1) | (mask_clean > 7)):
            logger.warning("Sample %s contains out-of-range mask values: %s", sample_id, np.unique(mask_clean))
            mask_clean = np.clip(mask_clean, 1, 7)

        target_tensor = torch.from_numpy(mask_clean - 1)  # 0 to 6 for CrossEntropyLoss

        return img_tensor, target_tensor, sample_id
