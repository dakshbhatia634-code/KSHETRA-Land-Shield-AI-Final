"""
Visual Calibrator for Pand Shield AI.

Generates visual calibration composites (RGB, color-coded mask, alpha overlay)
and class legends to inspect satellite image-mask alignment and class boundaries.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ml.data.loaders.parquet_loader import ParquetSatelliteLoader, SatelliteSample

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# High-contrast color palette for classes 1-7 (0 is unassigned/background)
CLASS_COLOR_PALETTE: Dict[int, Tuple[int, int, int]] = {
    1: (0, 119, 182),     # Blue
    2: (45, 106, 79),     # Deep Green
    3: (72, 202, 228),    # Cyan / Light Blue
    4: (116, 198, 157),   # Sage / Olive Green
    5: (255, 183, 3),     # Amber / Gold
    6: (203, 153, 126),   # Terra Cotta / Sand
    7: (157, 78, 221),    # Purple / Magenta
}


class VisualCalibrator:
    """
    Produces high-resolution visual calibration strips and palette legends.
    """

    def __init__(
        self,
        parquet_path: Union[str, Path] = "data/raw/train-00000-of-00007.parquet",
        output_dir: Union[str, Path] = "data/processed/calibration/visualizations",
    ):
        self.parquet_path = Path(parquet_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.loader = ParquetSatelliteLoader(self.parquet_path)

    def colorize_mask(self, mask: np.ndarray) -> Image.Image:
        """Converts a 2D integer mask (H, W) into an RGB Pillow Image."""
        h, w = mask.shape
        color_arr = np.zeros((h, w, 3), dtype=np.uint8)
        for class_id, color in CLASS_COLOR_PALETTE.items():
            color_arr[mask == class_id] = color
        return Image.fromarray(color_arr, mode="RGB")

    def create_calibration_strip(
        self, sample: SatelliteSample, upscale_size: int = 256
    ) -> Image.Image:
        """
        Creates a 3-panel composite: [Original RGB | Colorized Mask | Alpha Overlay].
        """
        rgb_img = Image.fromarray(sample.image, mode="RGB")
        mask_img = self.colorize_mask(sample.mask)

        # Alpha blend overlay (55% RGB + 45% Mask)
        overlay_img = Image.blend(rgb_img, mask_img, alpha=0.45)

        # Upscale with NEAREST so pixel boundaries remain crisp
        rgb_large = rgb_img.resize((upscale_size, upscale_size), Image.Resampling.NEAREST)
        mask_large = mask_img.resize((upscale_size, upscale_size), Image.Resampling.NEAREST)
        overlay_large = overlay_img.resize((upscale_size, upscale_size), Image.Resampling.NEAREST)

        # Layout canvas: 3 panels + header + padding
        pad = 12
        header_h = 38
        width = upscale_size * 3 + pad * 4
        height = upscale_size + header_h + pad * 2

        canvas = Image.new("RGB", (width, height), color=(248, 249, 250))
        draw = ImageDraw.Draw(canvas)

        # Draw panel titles
        draw.text((pad, 10), f"SAMPLE: {sample.sample_id}  |  PANEL 1: SATELLITE RGB (10m)", fill=(33, 37, 41))
        draw.text((pad * 2 + upscale_size, 10), "PANEL 2: SEMANTIC MASK (IDs 1-7)", fill=(33, 37, 41))
        draw.text((pad * 3 + upscale_size * 2, 10), "PANEL 3: BLENDED OVERLAY (55% / 45%)", fill=(33, 37, 41))

        # Paste images
        canvas.paste(rgb_large, (pad, header_h))
        canvas.paste(mask_large, (pad * 2 + upscale_size, header_h))
        canvas.paste(overlay_large, (pad * 3 + upscale_size * 2, header_h))

        return canvas

    def generate_calibration_samples(
        self, sample_indices: List[int]
    ) -> List[Path]:
        """Generates and saves calibration strip images for specified row indices."""
        saved_paths = []
        for idx in sample_indices:
            sample = self.loader.get_sample_by_index(idx)
            strip = self.create_calibration_strip(sample)
            clean_name = sample.sample_id.replace(".png", "")
            out_file = self.output_dir / f"calibration_tile_{idx:05d}_{clean_name}.png"
            strip.save(out_file)
            logger.info("Saved calibration strip: %s", out_file.name)
            saved_paths.append(out_file)
        return saved_paths

    def generate_palette_legend(
        self, class_frequencies: Dict[int, float]
    ) -> Path:
        """
        Creates a visual legend image displaying numeric class IDs and swatches.
        """
        width = 640
        row_height = 44
        header_h = 60
        height = header_h + row_height * len(CLASS_COLOR_PALETTE) + 20

        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(canvas := img)

        draw.text((20, 16), "LAND SHIELD AI — SEMANTIC MASK CALIBRATION LEGEND", fill=(17, 24, 39))
        draw.text((20, 36), "Strict Zero-Fabrication: Class IDs reported numerically until ground truth calibration", fill=(107, 114, 128))

        y = header_h
        for class_id in sorted(CLASS_COLOR_PALETTE.keys()):
            color = CLASS_COLOR_PALETTE[class_id]
            pct = class_frequencies.get(class_id, 0.0)

            # Draw swatch rectangle
            draw.rectangle([20, y + 6, 56, y + 32], fill=color, outline=(0, 0, 0))

            # Draw descriptive text
            label_text = f"Class {class_id}  |  Palette RGB: {color}  |  Frequency: {pct:.2f}%  |  Status: NUMERIC_ID_ONLY"
            draw.text((70, y + 10), label_text, fill=(31, 41, 55))

            y += row_height

        out_path = self.output_dir / "tile_calibration_legend.png"
        img.save(out_path)
        logger.info("Saved calibration palette legend: %s", out_path.name)
        return out_path
