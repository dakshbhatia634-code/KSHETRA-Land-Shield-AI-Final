"""
Parquet Satellite Dataset Loader for Pand Shield AI.

Provides safe, streaming access to satellite image-mask pairs stored
inside Apache Parquet shards without loading full datasets into memory.
"""

import io
import logging
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Tuple, Union

import numpy as np
import pyarrow.parquet as pq

# Configure structured logging
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
class SatelliteSample:
    """Represents a validated satellite image tile and its segmentation mask."""

    sample_id: str
    image: np.ndarray  # Shape: (height, width, 3), dtype: uint8
    mask: np.ndarray  # Shape: (height, width), dtype: uint8
    split: str
    metadata: Dict[str, Any]


def decode_png_rgb(png_bytes: bytes) -> np.ndarray:
    """
    Decodes an RGB PNG image from raw bytes into a NumPy array (H, W, 3).

    Uses Pillow if installed; otherwise falls back to a built-in standard library
    zlib/NumPy PNG decompressor to avoid hard external dependencies.
    """
    # 1. Fast path: Use Pillow if available in environment
    try:
        from PIL import Image

        with Image.open(io.BytesIO(png_bytes)) as pil_img:
            return np.array(pil_img.convert("RGB"), dtype=np.uint8)
    except ImportError:
        pass

    # 2. Pure Python / NumPy fallback decoder
    if png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Invalid PNG header signature")

    offset = 8
    idat_chunks = []
    width, height = 0, 0

    while offset < len(png_bytes):
        length, chunk_type = struct.unpack(">I4s", png_bytes[offset : offset + 8])
        chunk_data = png_bytes[offset + 8 : offset + 8 + length]
        offset += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(
                ">IIBB", chunk_data[:10]
            )
            if bit_depth != 8 or color_type not in (2, 6):
                raise ValueError(
                    f"Unsupported PNG format: bit_depth={bit_depth}, color_type={color_type}"
                )
        elif chunk_type == b"IDAT":
            idat_chunks.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width == 0 or height == 0:
        raise ValueError("Could not read PNG dimensions from IHDR")

    decompressed = zlib.decompress(b"".join(idat_chunks))
    bpp = 3  # RGB 8-bit
    stride = 1 + width * bpp
    img = np.zeros((height, width, bpp), dtype=np.uint8)
    prev_row = np.zeros(width * bpp, dtype=np.int32)

    for y in range(height):
        line = decompressed[y * stride : (y + 1) * stride]
        filter_type = line[0]
        curr = np.frombuffer(line[1:], dtype=np.uint8).astype(np.int32).copy()

        if filter_type == 0:  # None
            pass
        elif filter_type == 1:  # Sub
            for i in range(bpp, len(curr)):
                curr[i] = (curr[i] + curr[i - bpp]) & 0xFF
        elif filter_type == 2:  # Up
            curr = (curr + prev_row) & 0xFF
        elif filter_type == 3:  # Average
            for i in range(len(curr)):
                left = curr[i - bpp] if i >= bpp else 0
                up = prev_row[i]
                curr[i] = (curr[i] + ((left + up) >> 1)) & 0xFF
        elif filter_type == 4:  # Paeth
            for i in range(len(curr)):
                a = curr[i - bpp] if i >= bpp else 0
                b = prev_row[i]
                c = prev_row[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa = abs(p - a)
                pb = abs(p - b)
                pc = abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                curr[i] = (curr[i] + pr) & 0xFF
        else:
            raise ValueError(f"Unknown PNG filter type: {filter_type}")

        img[y] = (curr & 0xFF).astype(np.uint8).reshape((width, bpp))
        prev_row = curr

    return img


def decode_geotiff_mask(
    mask_bytes: bytes,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Decodes an uncompressed GeoTIFF semantic mask and extracts spatial metadata.

    Returns:
        (mask_array, metadata_dict) where mask_array is of shape (H, W).
    """
    if mask_bytes[:2] not in (b"II", b"MM"):
        raise ValueError("Invalid TIFF byte order header")

    endian = "<" if mask_bytes[:2] == b"II" else ">"
    offset = struct.unpack(endian + "I", mask_bytes[4:8])[0]
    num_tags = struct.unpack(endian + "H", mask_bytes[offset : offset + 2])[0]
    offset += 2

    metadata: Dict[str, Any] = {}
    strip_offset = None
    strip_bytes = None
    width, height = 64, 64

    for _ in range(num_tags):
        tag, typ, cnt, val = struct.unpack(
            endian + "HHI4s", mask_bytes[offset : offset + 12]
        )
        offset += 12

        if tag == 256:  # ImageWidth
            width = (
                struct.unpack(endian + "H", val[:2])[0]
                if typ == 3
                else struct.unpack(endian + "I", val)[0]
            )
        elif tag == 257:  # ImageLength
            height = (
                struct.unpack(endian + "H", val[:2])[0]
                if typ == 3
                else struct.unpack(endian + "I", val)[0]
            )
        elif tag == 273:  # StripOffsets
            strip_offset = struct.unpack(endian + "I", val)[0]
        elif tag == 279:  # StripByteCounts
            strip_bytes = struct.unpack(endian + "I", val)[0]
        elif tag == 33550:  # ModelPixelScaleTag
            scale_offset = struct.unpack(endian + "I", val)[0]
            scale = struct.unpack(
                endian + "3d", mask_bytes[scale_offset : scale_offset + 24]
            )
            metadata["pixel_scale"] = scale
        elif tag == 33922:  # ModelTiepointTag
            tie_offset = struct.unpack(endian + "I", val)[0]
            tiepoint = struct.unpack(
                endian + "6d", mask_bytes[tie_offset : tie_offset + 48]
            )
            metadata["tiepoint"] = tiepoint
        elif tag == 34737:  # GeoAsciiParamsTag
            ascii_offset = struct.unpack(endian + "I", val)[0]
            crs_str = mask_bytes[ascii_offset : ascii_offset + cnt].decode(
                "latin-1", errors="ignore"
            )
            metadata["crs_ascii"] = crs_str.rstrip("\x00|")

    if strip_offset is None or strip_bytes is None:
        raise ValueError("TIFF missing strip offset or byte count tags")

    raw_data = mask_bytes[strip_offset : strip_offset + strip_bytes]
    mask = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width))
    return mask, metadata


class ParquetSatelliteLoader:
    """
    Streaming loader for Sentinel-2 satellite image-mask Parquet shards.

    Streams rows in manageable chunks without reading the full file into memory.
    """

    def __init__(
        self,
        parquet_path: Union[str, Path],
        expected_shape: Tuple[int, int] = (64, 64),
    ):
        self.parquet_path = Path(parquet_path)
        if not self.parquet_path.is_file():
            raise FileNotFoundError(f"Parquet file not found at: {self.parquet_path}")

        self.expected_shape = expected_shape
        self._parquet_file = pq.ParquetFile(str(self.parquet_path))
        self.num_rows = self._parquet_file.metadata.num_rows
        self.num_row_groups = self._parquet_file.num_row_groups

        logger.info(
            "Initialized ParquetSatelliteLoader for %s: %d rows, %d row groups",
            self.parquet_path.name,
            self.num_rows,
            self.num_row_groups,
        )

    def stream_samples(
        self,
        batch_size: int = 100,
        max_samples: Optional[int] = None,
    ) -> Generator[SatelliteSample, None, None]:
        """
        Yields decoded SatelliteSample objects one by one using chunked reads.
        """
        yielded = 0
        for rg_idx in range(self.num_row_groups):
            table = self._parquet_file.read_row_group(rg_idx)
            df_chunk = table.to_pandas()

            for _, row in df_chunk.iterrows():
                try:
                    rgb_info = row.get("rgb", {})
                    mask_info = row.get("mask", {})
                    split = row.get("split", "unknown")

                    sample_id = rgb_info.get("path", f"row_{yielded}")
                    rgb_bytes = rgb_info.get("bytes")
                    mask_bytes = mask_info.get("bytes")

                    if rgb_bytes is None or mask_bytes is None:
                        logger.warning("Skipping sample %s: Missing binary payload", sample_id)
                        continue

                    # Decode
                    image = decode_png_rgb(rgb_bytes)
                    mask, meta = decode_geotiff_mask(mask_bytes)

                    # Validate dimensions
                    if image.shape[:2] != self.expected_shape:
                        logger.warning(
                            "Sample %s image shape mismatch: %s != %s",
                            sample_id,
                            image.shape[:2],
                            self.expected_shape,
                        )
                        continue

                    if mask.shape != self.expected_shape:
                        logger.warning(
                            "Sample %s mask shape mismatch: %s != %s",
                            sample_id,
                            mask.shape,
                            self.expected_shape,
                        )
                        continue

                    yield SatelliteSample(
                        sample_id=sample_id,
                        image=image,
                        mask=mask,
                        split=split,
                        metadata=meta,
                    )
                    yielded += 1

                    if max_samples is not None and yielded >= max_samples:
                        return

                except Exception as err:
                    logger.error("Error decoding sample at index %d: %s", yielded, err)
                    continue

    def get_sample_by_index(self, index: int) -> SatelliteSample:
        """Retrieves a single sample by its row index without loading the entire file."""
        if index < 0 or index >= self.num_rows:
            raise IndexError(f"Index {index} out of bounds (0..{self.num_rows - 1})")

        # Find row group containing this index
        accum = 0
        for rg_idx in range(self.num_row_groups):
            rg_rows = self._parquet_file.metadata.row_group(rg_idx).num_rows
            if accum + rg_rows > index:
                local_idx = index - accum
                table = self._parquet_file.read_row_group(rg_idx)
                row = table.to_pandas().iloc[local_idx]

                sample_id = row["rgb"]["path"]
                image = decode_png_rgb(row["rgb"]["bytes"])
                mask, meta = decode_geotiff_mask(row["mask"]["bytes"])

                return SatelliteSample(
                    sample_id=sample_id,
                    image=image,
                    mask=mask,
                    split=row["split"],
                    metadata=meta,
                )
            accum += rg_rows

        raise RuntimeError(f"Could not locate sample at index {index}")
