"""
Command-Line Interface for Model Prediction in Land Shield AI.

Usage:
    python -m ml.inference.predict --image path/to/tile.png --output-dir data/processed/predictions/
    python -m ml.inference.predict --parquet-index 0 --output-dir data/processed/predictions/
"""

import argparse
import json
import logging
from pathlib import Path
import sys

from PIL import Image

from ml.data.loaders.parquet_loader import ParquetSatelliteLoader
from ml.inference.predictor import LandCoverPredictor

logger = logging.getLogger("inference_cli")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Land Shield AI - Satellite Land-Cover Model Inference"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--image",
        type=str,
        help="Path to satellite image tile file (PNG, JPG, TIFF).",
    )
    group.add_argument(
        "--parquet-index",
        type=int,
        help="Index of sample to extract directly from raw parquet dataset.",
    )

    parser.add_argument(
        "--parquet-path",
        type=str,
        default="data/raw/train-00000-of-00007.parquet",
        help="Path to raw dataset Parquet file (used if --parquet-index is specified).",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="data/processed/models/baseline_run/best_model.pt",
        help="Path to trained model checkpoint (.pt).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed/predictions",
        help="Output folder where predictions and visualizations are saved.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Compute device for inference.",
    )
    parser.add_argument(
        "--allow-resize",
        action="store_true",
        help="Allow resizing if input image is not exactly 64x64.",
    )
    parser.add_argument(
        "--upscale-factor",
        type=int,
        default=4,
        help="Upscale factor for generated visualization masks (default: 4 -> 256x256).",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # 1. Validate Checkpoint
    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.is_file():
        logger.error("Checkpoint not found at: %s", checkpoint_path)
        sys.exit(1)

    # 2. Initialize Predictor
    try:
        predictor = LandCoverPredictor(
            checkpoint_path=checkpoint_path,
            device=args.device,
        )
    except Exception as e:
        logger.error("Failed to initialize predictor: %s", e)
        sys.exit(1)

    # 3. Retrieve or Load Input Image
    if args.parquet_index is not None:
        p_path = Path(args.parquet_path)
        if not p_path.is_file():
            logger.error("Parquet dataset file not found: %s", p_path)
            sys.exit(1)

        loader = ParquetSatelliteLoader(p_path)
        sample = loader.get_sample_by_index(args.parquet_index)
        sample_img = Image.fromarray(sample.image, mode="RGB")
        sample_name = f"parquet_tile_{args.parquet_index:05d}_{sample.sample_id.replace('.png', '')}"
    else:
        sample_img = Path(args.image)
        sample_name = sample_img.stem

    # 4. Execute Prediction and Save
    try:
        summary = predictor.predict_and_save(
            image_input=sample_img,
            output_dir=args.output_dir,
            sample_name=sample_name,
            upscale_factor=args.upscale_factor,
            allow_resize=args.allow_resize,
        )
    except Exception as e:
        logger.error("Inference failed: %s", e)
        sys.exit(1)

    # 5. Print User-Facing Summary
    print("\n" + "=" * 65)
    print("LAND SHIELD AI — SATELLITE LAND-COVER PREDICTION RESULT")
    print("=" * 65)
    print(f"Sample Name:       {summary['sample_name']}")
    print(f"Inference Device:  {summary['device']}")
    print(f"Inference Latency: {summary['inference_time_ms']} ms")
    print(f"Model Checkpoint:  {checkpoint_path.name} (Epoch {summary['checkpoint_epoch']})")
    print(f"Validation mIoU:   {summary['best_val_miou']}")
    print("-" * 65)
    print("CLASS-WISE PIXEL BREAKDOWN:")
    print(f"{'Class':<12} {'Pixel Count':<14} {'Percentage':<12}")
    print("-" * 40)
    for class_key, stats in summary["class_breakdown"].items():
        print(f"{stats['class_name']:<12} {stats['pixel_count']:<14,d} {stats['percentage']:>6.2f}%")
    print("-" * 65)
    print("SAVED ARTIFACTS:")
    for key, path_str in summary["saved_files"].items():
        print(f"  [{key}]: {path_str}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
