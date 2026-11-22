"""
Loss Functions for Imbalanced Satellite Land-Cover Segmentation in Pand Shield AI.

Implements Combined Weighted Cross-Entropy and Multi-Class Dice Loss
specifically tailored to counter class imbalance without causing optimization instability.
"""

from typing import Optional, Sequence, Union
import torch
import torch.nn as nn
import torch.nn.functional as F

# Raw empirical class frequencies from Phase 4 Step 4 Audit (Classes 1..7 -> Indices 0..6)
# Class 1: 1.185%, Class 2: 1.390%, Class 3: 6.240%, Class 4: 11.750%,
# Class 5: 27.970%, Class 6: 47.742%, Class 7: 4.470%
EMPIRICAL_CLASS_FREQUENCIES = [0.01185, 0.01390, 0.06240, 0.11750, 0.27970, 0.47742, 0.04470]

# Softened inverse-frequency weights using cube-root scaling: w_c = 1 / (f_c ** (1/3)), normalized to mean 1.0.
# Max-to-min penalty ratio is reduced from 37.0:1 down to ~3.4:1.
# This prevents gradient overshoot and catastrophic class swing towards minority classes.
SOFTENED_CLASS_WEIGHTS = [1.63, 1.55, 0.94, 0.77, 0.58, 0.48, 1.05]

# Legacy raw inverse weights (retained for backward compatibility and audits)
LEGACY_RAW_WEIGHTS = [0.778, 0.718, 0.160, 0.085, 0.036, 0.021, 0.224]

DEFAULT_CLASS_WEIGHTS = SOFTENED_CLASS_WEIGHTS


class MulticlassDiceLoss(nn.Module):
    """
    Computes soft multi-class Dice loss for semantic segmentation.
    Penalizes boundary and region mismatches independent of class frequency.
    """

    def __init__(self, smooth: float = 1e-5, num_classes: int = 7):
        super().__init__()
        self.smooth = smooth
        self.num_classes = num_classes

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: Predicted raw logits of shape (B, num_classes, H, W).
            targets: Ground truth integer class targets (B, H, W) in {0, ..., num_classes - 1}.
        """
        probs = F.softmax(logits, dim=1)
        # One-hot encode targets: (B, H, W) -> (B, num_classes, H, W)
        targets_one_hot = F.one_hot(targets, num_classes=self.num_classes).permute(0, 3, 1, 2).float()

        dice_per_class = []
        for c in range(self.num_classes):
            p = probs[:, c, :, :]
            t = targets_one_hot[:, c, :, :]

            intersection = 2.0 * (p * t).sum(dim=(1, 2))
            union = p.sum(dim=(1, 2)) + t.sum(dim=(1, 2))
            dice = (intersection + self.smooth) / (union + self.smooth)
            dice_per_class.append(dice.mean())

        mean_dice = torch.stack(dice_per_class).mean()
        return 1.0 - mean_dice


class CombinedWeightedLoss(nn.Module):
    """
    Blended loss function: alpha * WeightedCrossEntropy + (1 - alpha) * DiceLoss.

    Directly mitigates severe class imbalance (Class 6 @ 47.7% vs Class 1 @ 1.18%)
    using softened weighting to avoid gradient overshooting.
    """

    def __init__(
        self,
        class_weights: Optional[Union[torch.Tensor, Sequence[float]]] = None,
        alpha: float = 0.5,
        num_classes: int = 7,
        weighting_mode: str = "softened",
    ):
        super().__init__()
        self.alpha = alpha
        self.num_classes = num_classes

        if class_weights is not None:
            if isinstance(class_weights, (list, tuple)):
                w = torch.tensor(class_weights, dtype=torch.float32)
            else:
                w = class_weights.clone().detach().float()
            # Normalize to mean 1.0
            w = w / w.sum() * num_classes
            self.register_buffer("class_weights", w)
        elif weighting_mode == "softened":
            w = torch.tensor(SOFTENED_CLASS_WEIGHTS, dtype=torch.float32)
            w = w / w.sum() * num_classes
            self.register_buffer("class_weights", w)
        elif weighting_mode == "raw":
            w = torch.tensor(LEGACY_RAW_WEIGHTS, dtype=torch.float32)
            w = w / w.sum() * num_classes
            self.register_buffer("class_weights", w)
        elif weighting_mode == "none":
            w = torch.ones(num_classes, dtype=torch.float32)
            self.register_buffer("class_weights", w)
        else:
            raise ValueError(f"Unknown weighting_mode: {weighting_mode}")

        self.ce_loss = nn.CrossEntropyLoss(weight=self.class_weights)
        self.dice_loss = MulticlassDiceLoss(num_classes=num_classes)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Computes blended loss.
        """
        ce = self.ce_loss(logits, targets)
        dice = self.dice_loss(logits, targets)
        return self.alpha * ce + (1.0 - self.alpha) * dice

