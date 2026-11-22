"""
Core Inference Engine for Satellite Land-Cover Segmentation in Land Shield AI.

Loads the trained SatelliteUNet checkpoint, performs multi-spectral / RGB preprocessing,
computes 7-class segmentation predictions, and generates color-coded visualizations,
side-by-side composites, and pixel statistics.
"""

from dataclasses import asdict, dataclass
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
import torch.nn.functional as F

from ml.models.unet import SatelliteUNet

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# High-contrast color palette for classes 1-7 (consistent with Phase 4 Calibration)
CLASS_COLOR_PALETTE: Dict[int, Tuple[int, int, int]] = {
    1: (0, 119, 182),     # Blue (Water / Moist)
    2: (45, 106, 79),     # Deep Green (Dense Vegetation)
    3: (72, 202, 228),    # Cyan / Light Blue (Light Vegetation)
    4: (116, 198, 157),   # Sage / Olive Green (Agriculture / Crop)
    5: (255, 183, 3),     # Amber / Gold (Bare Soil / Sand)
    6: (203, 153, 126),   # Terra Cotta / Sand (Urban / Built-up)
    7: (157, 78, 221),    # Purple / Magenta (Dark / Shadow)
}

CLASS_SPECTRAL_DESCRIPTIONS: Dict[int, str] = {
    1: "Water / High Moisture Absorption",
    2: "Dense Vegetative Canopy",
    3: "Light Vegetation / Sparse Canopy",
    4: "Cultivated Crop / Agricultural Canopy",
    5: "Exposed Earth / Bare Soil",
    6: "Built-up / High Reflectance Impervious",
    7: "Deep Shadow / Low Albedo Feature",
}

# ImageNet / Sentinel-2 standard normalization parameters
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


@dataclass
class PredictionResult:
    """Encapsulates the complete result of an inference pass."""
    sample_name: str
    predicted_mask: np.ndarray          # 2D array (H, W) with class IDs 1..7
    confidence_map: np.ndarray          # 2D array (H, W) with softmax confidence [0, 1]
    mean_confidence_pct: float          # Average softmax confidence across all pixels
    colorized_mask: Image.Image         # RGB Pillow Image
    side_by_side: Image.Image           # 3-panel composite [RGB | Prediction | Overlay]
    legend_image: Image.Image           # Visual legend with swatches and percentages
    class_breakdown: Dict[str, Any]     # Per-class counts and percentages
    inference_time_ms: float
    device: str
    checkpoint_epoch: Optional[int] = None
    best_val_miou: Optional[float] = None


class LandCoverPredictor:
    """
    Production-grade inference pipeline for Land Shield AI.
    Handles checkpoint loading, input validation, GPU/CPU inference,
    and structured visual/tabular artifact creation.
    """

    def __init__(
        self,
        checkpoint_path: Union[str, Path] = "data/processed/models/baseline_run/best_model.pt",
        device: str = "auto",
        base_features: int = 32,
    ):
        self.checkpoint_path = Path(checkpoint_path)
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Model checkpoint not found at: {self.checkpoint_path}. "
                "Ensure that the model training has completed and generated best_model.pt."
            )

        # 1. Device selection (CUDA preferred with CPU fallback)
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        logger.info("Initializing LandCoverPredictor on device: %s", self.device)

        # 2. Instantiate Architecture
        self.model = SatelliteUNet(
            in_channels=3,
            num_classes=7,
            base_features=base_features,
        )

        # 3. Load Model Weights
        logger.info("Loading checkpoint from %s...", self.checkpoint_path.name)
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.checkpoint_epoch = checkpoint.get("epoch")
            val_metrics = checkpoint.get("val_metrics", {})
            self.best_val_miou = val_metrics.get("mean_iou")
            logger.info(
                "Loaded state_dict from Epoch %s (Validation mIoU: %s)",
                self.checkpoint_epoch,
                self.best_val_miou,
            )
        else:
            self.model.load_state_dict(checkpoint)
            self.checkpoint_epoch = None
            self.best_val_miou = None

        self.model.to(self.device)
        self.model.eval()

    def preprocess_image(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        allow_resize: bool = False,
    ) -> Tuple[torch.Tensor, np.ndarray, Image.Image]:
        """
        Loads, validates, and normalizes a satellite image tile.

        Returns:
            tensor: torch.FloatTensor of shape (1, 3, 64, 64) standardized on device
            rgb_arr: uint8 numpy array of shape (64, 64, 3)
            pil_img: PIL Image in RGB mode (64, 64)
        """
        # Load image if filepath provided
        if isinstance(image_input, (str, Path)):
            img_path = Path(image_input)
            if not img_path.is_file():
                raise FileNotFoundError(f"Image file does not exist: {img_path}")
            try:
                pil_img = Image.open(img_path)
                pil_img.load()
            except Exception as e:
                raise ValueError(f"Failed to read or decode image file '{img_path}': {e}") from e
        elif isinstance(image_input, Image.Image):
            pil_img = image_input
        elif isinstance(image_input, np.ndarray):
            if image_input.ndim != 3 or image_input.shape[2] != 3:
                raise ValueError(
                    f"NumPy image array must be shape (H, W, 3), got {image_input.shape}"
                )
            pil_img = Image.fromarray(image_input.astype(np.uint8), mode="RGB")
        else:
            raise TypeError(
                f"Unsupported image input type: {type(image_input)}. "
                "Expected file path (str/Path), PIL.Image, or numpy.ndarray."
            )

        # Ensure RGB format
        if pil_img.mode != "RGB":
            logger.warning("Input image mode '%s' converted to 'RGB'.", pil_img.mode)
            pil_img = pil_img.convert("RGB")

        # Validate resolution
        if pil_img.size != (64, 64):
            if allow_resize:
                logger.warning(
                    "Resizing input image from %s to expected 64x64.", pil_img.size
                )
                pil_img = pil_img.resize((64, 64), Image.Resampling.BILINEAR)
            else:
                raise ValueError(
                    f"Unsupported image dimensions: {pil_img.size}. "
                    "Expected a 64x64 satellite tile. "
                    "Pass allow_resize=True to automatically resample the input image."
                )

        rgb_arr = np.array(pil_img, dtype=np.uint8)

        # Standardize: [0, 255] -> [0, 1] -> (x - mean) / std
        norm_img = rgb_arr.astype(np.float32) / 255.0
        norm_img = (norm_img - IMAGENET_MEAN) / IMAGENET_STD

        # Transpose: (H, W, C) -> (C, H, W) -> (1, C, H, W)
        tensor = torch.from_numpy(norm_img).permute(2, 0, 1).unsqueeze(0).float()
        tensor = tensor.to(self.device)

        return tensor, rgb_arr, pil_img

    def colorize_mask(self, mask: np.ndarray) -> Image.Image:
        """Converts a 2D integer mask (H, W) into an RGB Pillow Image."""
        h, w = mask.shape
        color_arr = np.zeros((h, w, 3), dtype=np.uint8)
        for class_id, color in CLASS_COLOR_PALETTE.items():
            color_arr[mask == class_id] = color
        return Image.fromarray(color_arr, mode="RGB")

    def create_side_by_side_composite(
        self,
        rgb_img: Image.Image,
        predicted_mask: np.ndarray,
        sample_name: str = "Satellite Tile",
        upscale_size: int = 256,
        alpha: float = 0.45,
    ) -> Image.Image:
        """
        Creates a crisp 3-panel visualization:
        [Original Satellite RGB | Predicted Land-Cover | Blended Overlay]
        """
        color_mask_img = self.colorize_mask(predicted_mask)

        # Upscale for clear display
        rgb_large = rgb_img.resize((upscale_size, upscale_size), Image.Resampling.NEAREST)
        mask_large = color_mask_img.resize((upscale_size, upscale_size), Image.Resampling.NEAREST)
        overlay_large = Image.blend(rgb_large, mask_large, alpha=alpha)

        pad = 12
        header_h = 44
        canvas_w = upscale_size * 3 + pad * 4
        canvas_h = upscale_size + header_h + pad * 2

        composite = Image.new("RGB", (canvas_w, canvas_h), color=(248, 249, 250))
        draw = ImageDraw.Draw(composite)

        # Draw panel titles
        draw.text((pad, 12), f"ORIGINAL RGB (10m) — {sample_name}", fill=(33, 37, 41))
        draw.text((pad * 2 + upscale_size, 12), "PREDICTED LAND-COVER (Classes 1-7)", fill=(33, 37, 41))
        draw.text((pad * 3 + upscale_size * 2, 12), f"BLENDED OVERLAY ({int((1-alpha)*100)}% / {int(alpha*100)}%)", fill=(33, 37, 41))

        # Paste panels
        composite.paste(rgb_large, (pad, header_h))
        composite.paste(mask_large, (pad * 2 + upscale_size, header_h))
        composite.paste(overlay_large, (pad * 3 + upscale_size * 2, header_h))

        return composite

    def create_legend_image(
        self,
        class_breakdown: Dict[str, Any],
        sample_name: str = "Sample",
    ) -> Image.Image:
        """
        Renders a standalone visual legend showing color swatches,
        class numeric labels, and detected pixel percentages.
        """
        width = 540
        row_height = 36
        header_h = 56
        height = header_h + row_height * len(CLASS_COLOR_PALETTE) + 16

        legend_img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(legend_img)

        # Title
        draw.text((16, 12), f"LAND-COVER PREDICTION BREAKDOWN: {sample_name}", fill=(17, 24, 39))
        draw.text((16, 32), "7-Class Spectral Classification (SatelliteUNet)", fill=(107, 114, 128))

        y = header_h
        for class_id in sorted(CLASS_COLOR_PALETTE.keys()):
            color = CLASS_COLOR_PALETTE[class_id]
            stats = class_breakdown.get(f"class_{class_id}", {})
            pct = stats.get("percentage", 0.0)
            count = stats.get("pixel_count", 0)

            # Draw colored swatch
            draw.rectangle([16, y + 4, 48, y + 26], fill=color, outline=(209, 213, 219))

            # Class label and metrics
            label_text = f"Class {class_id} (Numeric ID: {class_id})"
            stats_text = f"{pct:6.2f}%  ({count:,} px)"
            draw.text((60, y + 7), label_text, fill=(31, 41, 55))
            draw.text((360, y + 7), stats_text, fill=(55, 65, 81))

            y += row_height

        return legend_img

    def predict(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        sample_name: Optional[str] = None,
        allow_resize: bool = False,
    ) -> PredictionResult:
        """
        Executes end-to-end land-cover inference on a single satellite tile.
        """
        if sample_name is None:
            if isinstance(image_input, (str, Path)):
                sample_name = Path(image_input).name
            else:
                sample_name = "Satellite Tile"

        t0 = time.time()
        tensor, rgb_arr, pil_img = self.preprocess_image(image_input, allow_resize=allow_resize)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1)
            # Predicted class IDs: argmax (0..6) + 1 -> (1..7)
            pred_indices = torch.argmax(logits, dim=1)
            pred_mask = (pred_indices + 1).squeeze(0).cpu().numpy().astype(np.uint8)
            conf_map = torch.max(probs, dim=1)[0].squeeze(0).cpu().numpy()

        elapsed_ms = (time.time() - t0) * 1000.0

        # Class breakdown calculation
        total_pixels = pred_mask.size
        class_breakdown = {}
        for class_id in range(1, 8):
            count = int(np.sum(pred_mask == class_id))
            pct = round((count / total_pixels) * 100.0, 2)
            class_breakdown[f"class_{class_id}"] = {
                "class_id": class_id,
                "class_name": f"Class {class_id}",
                "spectral_description": CLASS_SPECTRAL_DESCRIPTIONS.get(class_id, "Spectral Signature"),
                "pixel_count": count,
                "percentage": pct,
                "color_rgb": list(CLASS_COLOR_PALETTE[class_id]),
            }

        # Visualizations
        color_mask = self.colorize_mask(pred_mask)
        side_by_side = self.create_side_by_side_composite(pil_img, pred_mask, sample_name=sample_name)
        legend_img = self.create_legend_image(class_breakdown, sample_name=sample_name)
        mean_conf = round(float(np.mean(conf_map)) * 100.0, 2)

        return PredictionResult(
            sample_name=sample_name,
            predicted_mask=pred_mask,
            confidence_map=conf_map,
            mean_confidence_pct=mean_conf,
            colorized_mask=color_mask,
            side_by_side=side_by_side,
            legend_image=legend_img,
            class_breakdown=class_breakdown,
            inference_time_ms=round(elapsed_ms, 2),
            device=str(self.device),
            checkpoint_epoch=self.checkpoint_epoch,
            best_val_miou=self.best_val_miou,
        )

    def predict_and_save(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        output_dir: Union[str, Path] = "data/processed/predictions",
        sample_name: Optional[str] = None,
        upscale_factor: int = 4,
        allow_resize: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes inference and writes all artifacts to disk:
        - predicted_mask.png (raw integer IDs 1..7)
        - colorized_mask.png (color-coded visualization)
        - side_by_side_comparison.png (3-panel visual composite)
        - legend.png (class breakdown legend)
        - prediction_summary.json (structured metrics and metadata)
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        if sample_name is None:
            if isinstance(image_input, (str, Path)):
                stem = Path(image_input).stem
            else:
                stem = f"tile_{int(time.time())}"
        else:
            stem = sample_name.replace(".png", "").replace(".jpg", "").replace(".tif", "")

        res = self.predict(image_input, sample_name=stem, allow_resize=allow_resize)

        # 1. Save raw integer mask (values 1..7)
        mask_path = out_path / f"{stem}_predicted_mask.png"
        raw_mask_pil = Image.fromarray(res.predicted_mask, mode="L")
        raw_mask_pil.save(mask_path)

        # 2. Save colorized mask (upscaled for display clarity)
        color_path = out_path / f"{stem}_colorized_mask.png"
        upscale_size = (64 * upscale_factor, 64 * upscale_factor)
        res.colorized_mask.resize(upscale_size, Image.Resampling.NEAREST).save(color_path)

        # 3. Save side-by-side composite
        side_path = out_path / f"{stem}_side_by_side.png"
        res.side_by_side.save(side_path)

        # 4. Save visual legend
        legend_path = out_path / f"{stem}_legend.png"
        res.legend_image.save(legend_path)

        # 5. Save structured JSON summary
        summary_path = out_path / f"{stem}_summary.json"
        summary_data = {
            "sample_name": stem,
            "inference_time_ms": res.inference_time_ms,
            "device": res.device,
            "checkpoint_epoch": res.checkpoint_epoch,
            "best_val_miou": res.best_val_miou,
            "class_breakdown": res.class_breakdown,
            "saved_files": {
                "predicted_mask": str(mask_path),
                "colorized_mask": str(color_path),
                "side_by_side": str(side_path),
                "legend": str(legend_path),
            },
        }
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        logger.info("Saved inference outputs to: %s", out_path)
        return summary_data
