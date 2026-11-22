"""
Command-Line Interface for Training Satellite Land-Cover Segmentation in Pand Shield AI.

Reproducible training script with configurable hyperparameters,
spatial group train/val splitting, and automated checkpoint tracking.
"""

import argparse
import json
import logging
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ml.data.dataset import SatelliteSegmentationDataset
from ml.data.spatial_split import SpatialSplitEngine
from ml.models.unet import SatelliteUNet
from ml.training.losses import CombinedWeightedLoss
from ml.training.trainer import SegmentationTrainer

logger = logging.getLogger("train")
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
        description="Pand Shield AI - Satellite Land-Cover U-Net Training Pipeline"
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Mini-batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Initial learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="AdamW weight decay")
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience")
    parser.add_argument("--block-size-km", type=float, default=20.0, help="Spatial block size in km")
    parser.add_argument("--val-ratio", type=float, default=0.20, help="Validation ratio")
    parser.add_argument("--sample-limit", type=int, default=None, help="Optional sample limit for quick test runs")
    parser.add_argument("--cache-in-memory", action="store_true", help="Cache dataset in memory for speed")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu"], help="Training hardware")
    parser.add_argument("--checkpoint-dir", type=str, default="data/processed/models", help="Output directory")
    parser.add_argument("--base-features", type=int, default=32, help="Base features in U-Net first layer")
    parser.add_argument(
        "--weighting-mode",
        type=str,
        default="softened",
        choices=["softened", "raw", "none"],
        help="Class weighting scheme for Cross-Entropy loss",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info("=== PAND SHIELD AI — SATELLITE SEGMENTATION PIPELINE ===")
    logger.info("Arguments: %s", vars(args))

    # 1. Device Selection
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    logger.info("Selected computation device: %s", device)

    # 2. Spatially Grouped Train/Val Split
    logger.info("Computing spatial block partition (block size: %.1f km)...", args.block_size_km)
    split_engine = SpatialSplitEngine(
        block_size_km=args.block_size_km,
        val_ratio=args.val_ratio,
        random_seed=42,
    )
    train_indices, val_indices, split_meta = split_engine.compute_spatial_split()
    logger.info("Spatial split: %d train tiles | %d val tiles", len(train_indices), len(val_indices))

    # Optional sample limiting (for quick experiments)
    if args.sample_limit:
        train_indices = train_indices[: int(args.sample_limit * (1.0 - args.val_ratio))]
        val_indices = val_indices[: int(args.sample_limit * args.val_ratio)]
        logger.info("Sample limit applied: %d train | %d val", len(train_indices), len(val_indices))

    # 3. PyTorch Datasets & DataLoaders
    train_dataset = SatelliteSegmentationDataset(
        sample_indices=train_indices,
        cache_in_memory=args.cache_in_memory,
        normalize=True,
    )
    val_dataset = SatelliteSegmentationDataset(
        sample_indices=val_indices,
        cache_in_memory=args.cache_in_memory,
        normalize=True,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        drop_last=False,
    )

    # 4. Instantiate Model & Imbalance Loss
    model = SatelliteUNet(
        in_channels=3,
        num_classes=7,
        base_features=args.base_features,
    )
    criterion = CombinedWeightedLoss(
        num_classes=7,
        weighting_mode=args.weighting_mode,
    )

    # 5. Trainer Initialization & Execution
    trainer = SegmentationTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        device=device,
        checkpoint_dir=args.checkpoint_dir,
        patience=args.patience,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
    )

    train_results = trainer.train(num_epochs=args.epochs)
    logger.info("=== TRAINING COMPLETED ===")
    print("\n" + "=" * 60)
    print("FINAL TRAINING OUTCOME")
    print("=" * 60)
    print(json.dumps(train_results, indent=2))


if __name__ == "__main__":
    main()
