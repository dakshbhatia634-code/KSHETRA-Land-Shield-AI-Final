"""
Trainer Engine for Satellite Land-Cover Segmentation in Pand Shield AI.

Orchestrates GPU/CPU training, validation evaluation, metric accumulation,
early stopping, and atomic checkpoint persistence.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau
from torch.utils.data import DataLoader

from ml.models.unet import SatelliteUNet
from ml.training.losses import CombinedWeightedLoss
from ml.training.metrics import SegmentationMetrics

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class SegmentationTrainer:
    """
    Production-grade trainer for SatelliteUNet.
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: Optional[nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        device: Optional[Union[str, torch.device]] = None,
        checkpoint_dir: Union[str, Path] = "data/processed/models",
        patience: int = 5,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
    ):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader

        self.criterion = criterion or CombinedWeightedLoss()
        self.criterion = self.criterion.to(self.device)

        self.optimizer = optimizer or AdamW(
            self.model.parameters(), lr=learning_rate, weight_decay=weight_decay
        )
        self.scheduler = ReduceLROnPlateau(self.optimizer, mode="max", factor=0.5, patience=2)

        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.patience = patience
        self.metrics_evaluator = SegmentationMetrics(num_classes=7)

        self.history: List[Dict[str, Any]] = []
        self.best_val_miou: float = -1.0
        self.early_stop_counter: int = 0

        logger.info(
            "Initialized SegmentationTrainer on device: %s (Checkpoints: %s)",
            self.device,
            self.checkpoint_dir,
        )

    def train_epoch(self, epoch: int) -> float:
        """Runs one complete training epoch."""
        self.model.train()
        total_loss = 0.0
        batch_count = 0
        t0 = time.time()

        for batch_idx, (images, targets, _) in enumerate(self.train_loader):
            images = images.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)

            self.optimizer.zero_grad()
            logits = self.model(images)
            loss = self.criterion(logits, targets)

            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()
            batch_count += 1

        avg_loss = total_loss / max(1, batch_count)
        elapsed = time.time() - t0
        logger.info(
            "Epoch %d [Train] - Loss: %.4f | Time: %.1fs | Batches: %d",
            epoch,
            avg_loss,
            elapsed,
            batch_count,
        )
        return avg_loss

    def validate_epoch(self, epoch: int) -> Tuple[float, Dict[str, Any]]:
        """Runs validation evaluation and computes multi-class metrics."""
        self.model.eval()
        self.metrics_evaluator.reset()
        total_loss = 0.0
        batch_count = 0
        t0 = time.time()

        with torch.no_grad():
            for images, targets, _ in self.val_loader:
                images = images.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)

                logits = self.model(images)
                loss = self.criterion(logits, targets)

                total_loss += loss.item()
                batch_count += 1

                preds = torch.argmax(logits, dim=1)
                self.metrics_evaluator.update(preds, targets)

        avg_loss = total_loss / max(1, batch_count)
        metrics = self.metrics_evaluator.compute()
        elapsed = time.time() - t0

        logger.info(
            "Epoch %d [Val] - Loss: %.4f | mIoU: %.4f | Dice: %.4f | Acc: %.4f | Time: %.1fs",
            epoch,
            avg_loss,
            metrics["mean_iou"],
            metrics["mean_dice"],
            metrics["overall_accuracy"],
            elapsed,
        )
        return avg_loss, metrics

    def save_checkpoint(
        self,
        epoch: int,
        val_metrics: Dict[str, Any],
        filename: str = "best_model.pt",
    ) -> Path:
        """Saves model weights, optimizer state, and evaluation metrics."""
        save_path = self.checkpoint_dir / filename
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "val_metrics": val_metrics,
            "architecture": "SatelliteUNet",
            "num_classes": 7,
            "in_channels": 3,
        }
        torch.save(checkpoint, save_path)
        logger.info("Saved checkpoint: %s (val_mIoU: %.4f)", save_path.name, val_metrics["mean_iou"])
        return save_path

    def train(self, num_epochs: int = 10) -> Dict[str, Any]:
        """
        Executes full training loop with early stopping and checkpoint tracking.
        """
        logger.info("Starting training for %d epochs...", num_epochs)

        for epoch in range(1, num_epochs + 1):
            train_loss = self.train_epoch(epoch)
            val_loss, val_metrics = self.validate_epoch(epoch)

            # Update learning rate scheduler
            self.scheduler.step(val_metrics["mean_iou"])

            epoch_log = {
                "epoch": epoch,
                "train_loss": round(train_loss, 4),
                "val_loss": round(val_loss, 4),
                "val_metrics": val_metrics,
                "learning_rate": self.optimizer.param_groups[0]["lr"],
            }
            self.history.append(epoch_log)

            # Always save latest checkpoint
            self.save_checkpoint(epoch, val_metrics, filename="latest_checkpoint.pt")

            # Check for improvement (Early Stopping & Best Model Checkpoint)
            current_miou = val_metrics["mean_iou"]
            if current_miou > self.best_val_miou:
                logger.info(
                    "Validation mIoU improved from %.4f to %.4f",
                    self.best_val_miou,
                    current_miou,
                )
                self.best_val_miou = current_miou
                self.early_stop_counter = 0
                self.save_checkpoint(epoch, val_metrics, filename="best_model.pt")
            else:
                self.early_stop_counter += 1
                logger.info(
                    "No improvement in mIoU for %d epoch(s) (Patience: %d)",
                    self.early_stop_counter,
                    self.patience,
                )
                if self.early_stop_counter >= self.patience:
                    logger.info("Early stopping triggered at epoch %d.", epoch)
                    break

        # Save complete training history
        history_path = self.checkpoint_dir / "training_history.json"
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)
        logger.info("Saved complete training history to %s", history_path.name)

        return {
            "best_val_miou": self.best_val_miou,
            "total_epochs_trained": len(self.history),
            "checkpoints": {
                "best_model": str(self.checkpoint_dir / "best_model.pt"),
                "latest_checkpoint": str(self.checkpoint_dir / "latest_checkpoint.pt"),
            },
        }
