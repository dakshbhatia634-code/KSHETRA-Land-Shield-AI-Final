"""
U-Net Segmentation Architecture for Pand Shield AI.

A modular, clean, and upgradeable baseline 2D convolutional neural network
designed for multi-class satellite land-cover semantic segmentation.
"""

from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):
    """[Conv2d -> BatchNorm2d -> ReLU] x 2 block."""

    def __init__(self, in_channels: int, out_channels: int, mid_channels: Optional[int] = None):
        super().__init__()
        if mid_channels is None:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with MaxPool2d then DoubleConv."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling with ConvTranspose2d, concatenating skip connection, then DoubleConv."""

    def __init__(self, in_channels: int, out_channels: int, bilinear: bool = False):
        super().__init__()
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        x1 = self.up(x1)
        # Pad x1 if necessary to match x2 spatial dimensions
        diff_y = x2.size()[2] - x1.size()[2]
        diff_x = x2.size()[3] - x1.size()[3]
        if diff_y != 0 or diff_x != 0:
            x1 = F.pad(x1, [diff_x // 2, diff_x - diff_x // 2, diff_y // 2, diff_y - diff_y // 2])

        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    """1x1 convolution mapping latent channels to target class logits."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class SatelliteUNet(nn.Module):
    """
    Modular U-Net model for multi-class satellite land-cover segmentation.

    Args:
        in_channels: Number of input spectral bands (default 3 for RGB).
        num_classes: Number of discrete land cover classes (default 7).
        base_features: Number of filters in the first conv layer (default 32).
        bilinear: Whether to use bilinear upsampling instead of transpose convolutions.
    """

    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 7,
        base_features: int = 32,
        bilinear: bool = False,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes
        self.bilinear = bilinear
        self.base_features = base_features

        f = base_features  # e.g., 32
        self.inc = DoubleConv(in_channels, f)
        self.down1 = Down(f, f * 2)        # 32 -> 64 (spatial: 32x32)
        self.down2 = Down(f * 2, f * 4)    # 64 -> 128 (spatial: 16x16)
        self.down3 = Down(f * 4, f * 8)    # 128 -> 256 (spatial: 8x8)
        factor = 2 if bilinear else 1
        self.down4 = Down(f * 8, f * 16 // factor)  # 256 -> 512 or 256 (spatial: 4x4)

        self.up1 = Up(f * 16, f * 8 // factor, bilinear)
        self.up2 = Up(f * 8, f * 4 // factor, bilinear)
        self.up3 = Up(f * 4, f * 2 // factor, bilinear)
        self.up4 = Up(f * 2, f, bilinear)
        self.outc = OutConv(f, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        Input: Tensor of shape (Batch, in_channels, Height, Width)
        Output: Raw logits of shape (Batch, num_classes, Height, Width)
        """
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits

    @staticmethod
    def decode_predictions(logits: torch.Tensor) -> torch.Tensor:
        """
        Converts raw model logits (B, 7, H, W) to 1-indexed class IDs (1-7).
        Zero-indexed argmax (0..6) + 1 -> (1..7).
        """
        pred_zero_indexed = torch.argmax(logits, dim=1)
        return pred_zero_indexed + 1
