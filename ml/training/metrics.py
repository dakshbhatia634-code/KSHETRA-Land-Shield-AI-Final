"""
Segmentation Evaluation Metrics for Pand Shield AI.

Computes exact multi-class metrics: Mean IoU, Per-Class IoU,
Dice Score, Overall Pixel Accuracy, and Confusion Matrix across classes 1-7.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import torch


class SegmentationMetrics:
    """
    Accumulates confusion matrix across evaluation batches and computes segmentation metrics.
    """

    def __init__(self, num_classes: int = 7):
        self.num_classes = num_classes
        self.reset()

    def reset(self) -> None:
        """Resets the confusion matrix accumulator."""
        self.confusion_matrix = np.zeros((self.num_classes, self.num_classes), dtype=np.int64)

    def update(self, preds: torch.Tensor, targets: torch.Tensor) -> None:
        """
        Updates the confusion matrix with a batch of predictions and targets.
        Args:
            preds: Tensor of predicted class indices (B, H, W) in {0, ..., num_classes - 1}.
            targets: Tensor of ground truth class indices (B, H, W) in {0, ..., num_classes - 1}.
        """
        preds_np = preds.detach().cpu().numpy().flatten()
        targets_np = targets.detach().cpu().numpy().flatten()

        mask = (targets_np >= 0) & (targets_np < self.num_classes)
        t_valid = targets_np[mask]
        p_valid = preds_np[mask]

        # Fast 2D bincount accumulation
        indices = t_valid * self.num_classes + p_valid
        counts = np.bincount(indices, minlength=self.num_classes**2)
        self.confusion_matrix += counts.reshape(self.num_classes, self.num_classes)

    def compute(self) -> Dict[str, Any]:
        """
        Computes final metrics from accumulated confusion matrix.
        Returns:
            Dictionary with overall accuracy, mIoU, mean Dice, per-class IoU,
            per-class Dice, and the confusion matrix.
        """
        cm = self.confusion_matrix
        total_pixels = cm.sum()

        if total_pixels == 0:
            return {
                "overall_accuracy": 0.0,
                "mean_iou": 0.0,
                "mean_dice": 0.0,
                "per_class_iou": {f"class_{c+1}": 0.0 for c in range(self.num_classes)},
                "per_class_dice": {f"class_{c+1}": 0.0 for c in range(self.num_classes)},
                "confusion_matrix": cm.tolist(),
            }

        diag = np.diag(cm)
        overall_accuracy = float(diag.sum() / total_pixels)

        # Per-class IoU = TP / (TP + FP + FN)
        # Row sum = TP + FN (Ground truth)
        # Col sum = TP + FP (Predicted)
        row_sums = cm.sum(axis=1)
        col_sums = cm.sum(axis=0)

        per_class_iou = {}
        per_class_dice = {}
        valid_ious = []
        valid_dices = []

        for c in range(self.num_classes):
            tp = float(diag[c])
            fp = float(col_sums[c] - tp)
            fn = float(row_sums[c] - tp)

            denom_iou = tp + fp + fn
            denom_dice = 2.0 * tp + fp + fn

            class_key = f"class_{c + 1}"  # 1-indexed for logging (1 to 7)

            if denom_iou > 0:
                iou = tp / denom_iou
                per_class_iou[class_key] = round(iou, 4)
                valid_ious.append(iou)
            else:
                per_class_iou[class_key] = float("nan")

            if denom_dice > 0:
                dice = (2.0 * tp) / denom_dice
                per_class_dice[class_key] = round(dice, 4)
                valid_dices.append(dice)
            else:
                per_class_dice[class_key] = float("nan")

        mean_iou = float(np.mean(valid_ious)) if valid_ious else 0.0
        mean_dice = float(np.mean(valid_dices)) if valid_dices else 0.0

        return {
            "overall_accuracy": round(overall_accuracy, 4),
            "mean_iou": round(mean_iou, 4),
            "mean_dice": round(mean_dice, 4),
            "per_class_iou": per_class_iou,
            "per_class_dice": per_class_dice,
            "confusion_matrix": cm.tolist(),
        }
