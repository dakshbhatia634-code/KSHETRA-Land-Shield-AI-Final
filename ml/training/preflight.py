"""
Preflight Verification Test for Pand Shield AI.

Systematically verifies data loading, image-mask alignment, class IDs,
tensor shapes, spatial split integrity, and model forward/backward pass.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import torch
from torch.utils.data import DataLoader

from ml.data.dataset import SatelliteSegmentationDataset
from ml.data.spatial_split import SpatialSplitEngine
from ml.models.unet import SatelliteUNet
from ml.training.losses import CombinedWeightedLoss
from ml.training.metrics import SegmentationMetrics

logger = logging.getLogger("preflight")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def run_preflight_test(
    output_report_path: str = "data/processed/models/preflight_test_report.json",
) -> Dict[str, Any]:
    """
    Executes comprehensive 8-step preflight verification checklist.
    """
    logger.info("=== STARTING PHASE 5 PREFLIGHT VERIFICATION TEST ===")
    test_results = {}
    all_passed = True

    # 1. Device Detection
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Test 1: Compute Device Detection -> %s", device)
    test_results["test_1_device"] = {
        "device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "status": "PASS",
    }

    # 2. Spatial Split Integrity & Leakage Check
    logger.info("Test 2: Verifying Spatial Group Split Integrity...")
    split_engine = SpatialSplitEngine(block_size_km=20.0, val_ratio=0.20, random_seed=42)
    train_idx, val_idx, meta = split_engine.compute_spatial_split()

    train_set = set(train_idx)
    val_set = set(val_idx)
    index_overlap = len(train_set.intersection(val_set))
    assert index_overlap == 0, f"Critical Leakage: {index_overlap} overlapping indices!"

    logger.info("  Train tiles: %d | Val tiles: %d | Overlap: %d", len(train_idx), len(val_idx), index_overlap)
    test_results["test_2_spatial_split"] = {
        "train_tiles": len(train_idx),
        "val_tiles": len(val_idx),
        "spatial_block_size_km": meta["block_size_km"],
        "overlapping_tiles": index_overlap,
        "status": "PASS",
    }

    # 3. Data Loading & Single Sample Format
    logger.info("Test 3: Verifying Dataset Loader and Sample Shapes...")
    dataset = SatelliteSegmentationDataset(sample_indices=train_idx[:20], normalize=True)
    img_tensor, mask_tensor, sample_id = dataset[0]

    assert img_tensor.shape == (3, 64, 64), f"Image shape mismatch: {img_tensor.shape}"
    assert mask_tensor.shape == (64, 64), f"Mask shape mismatch: {mask_tensor.shape}"
    assert img_tensor.dtype == torch.float32, f"Image dtype mismatch: {img_tensor.dtype}"
    assert mask_tensor.dtype == torch.int64, f"Mask dtype mismatch: {mask_tensor.dtype}"

    logger.info("  Sample %s: Image shape=%s, Mask shape=%s", sample_id, list(img_tensor.shape), list(mask_tensor.shape))
    test_results["test_3_sample_format"] = {
        "sample_id": sample_id,
        "image_shape": list(img_tensor.shape),
        "mask_shape": list(mask_tensor.shape),
        "image_dtype": str(img_tensor.dtype),
        "mask_dtype": str(mask_tensor.dtype),
        "status": "PASS",
    }

    # 4. Class ID Conversion & Range Check
    logger.info("Test 4: Verifying Class IDs (Internal: 0-6, Decoded: 1-7)...")
    unique_target_classes = torch.unique(mask_tensor).tolist()
    min_c = min(unique_target_classes)
    max_c = max(unique_target_classes)
    assert min_c >= 0 and max_c <= 6, f"Target classes out of 0-6 range: {unique_target_classes}"

    logger.info("  Zero-indexed target range: min=%d, max=%d (valid: 0..6)", min_c, max_c)
    test_results["test_4_class_ids"] = {
        "target_classes_found": unique_target_classes,
        "zero_indexed_range": [min_c, max_c],
        "status": "PASS",
    }

    # 5. Batch DataLoader Formation
    logger.info("Test 5: Testing Mini-Batch DataLoader (Batch size = 4)...")
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    batch_images, batch_masks, batch_ids = next(iter(loader))

    assert batch_images.shape == (4, 3, 64, 64), f"Batch images shape mismatch: {batch_images.shape}"
    assert batch_masks.shape == (4, 64, 64), f"Batch masks shape mismatch: {batch_masks.shape}"

    logger.info("  Batch images: %s, Batch masks: %s", list(batch_images.shape), list(batch_masks.shape))
    test_results["test_5_batching"] = {
        "batch_images_shape": list(batch_images.shape),
        "batch_masks_shape": list(batch_masks.shape),
        "status": "PASS",
    }

    # 6. Model Forward Pass & Logit Dimensions
    logger.info("Test 6: Testing SatelliteUNet Forward Pass on %s...", device)
    model = SatelliteUNet(in_channels=3, num_classes=7, base_features=32).to(device)
    batch_images_dev = batch_images.to(device)
    logits = model(batch_images_dev)

    assert logits.shape == (4, 7, 64, 64), f"Logits shape mismatch: {logits.shape}"
    decoded_preds = model.decode_predictions(logits)
    assert decoded_preds.shape == (4, 64, 64), f"Decoded preds shape mismatch: {decoded_preds.shape}"
    assert decoded_preds.min().item() >= 1 and decoded_preds.max().item() <= 7

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info("  Forward pass output: %s | Trainable parameters: %d", list(logits.shape), total_params)
    test_results["test_6_forward_pass"] = {
        "logits_shape": list(logits.shape),
        "decoded_preds_shape": list(decoded_preds.shape),
        "trainable_parameters": total_params,
        "status": "PASS",
    }

    # 7. Loss Computation & Backward Pass
    logger.info("Test 7: Testing Combined Weighted Loss & Gradient Backward Pass...")
    criterion = CombinedWeightedLoss(num_classes=7).to(device)
    batch_masks_dev = batch_masks.to(device)
    loss = criterion(logits, batch_masks_dev)

    assert torch.isfinite(loss), f"Loss is not finite: {loss.item()}"
    loss.backward()

    # Verify gradients exist on first conv layer
    first_conv_grad = model.inc.double_conv[0].weight.grad
    assert first_conv_grad is not None, "Gradients not computed for first conv layer!"
    assert torch.isfinite(first_conv_grad).all(), "Gradients contain NaN/Inf!"

    logger.info("  Computed loss: %.4f | Gradients verified successfully.", loss.item())
    test_results["test_7_loss_and_gradients"] = {
        "computed_loss": round(float(loss.item()), 4),
        "loss_is_finite": True,
        "gradients_verified": True,
        "status": "PASS",
    }

    # 8. Metrics Accumulator Verification
    logger.info("Test 8: Testing Multi-Class Segmentation Metrics Accumulation...")
    metrics_acc = SegmentationMetrics(num_classes=7)
    dummy_preds = torch.argmax(logits, dim=1)
    metrics_acc.update(dummy_preds, batch_masks_dev)
    computed_metrics = metrics_acc.compute()

    assert "mean_iou" in computed_metrics and "mean_dice" in computed_metrics
    assert "overall_accuracy" in computed_metrics and "confusion_matrix" in computed_metrics

    logger.info("  Metrics verified: mIoU=%.4f, Acc=%.4f", computed_metrics["mean_iou"], computed_metrics["overall_accuracy"])
    test_results["test_8_metrics"] = {
        "metrics_keys": list(computed_metrics.keys()),
        "confusion_matrix_shape": [len(computed_metrics["confusion_matrix"]), len(computed_metrics["confusion_matrix"][0])],
        "status": "PASS",
    }

    # Final Verdict
    out_path = Path(output_report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_report = {
        "preflight_verdict": "ALL_TESTS_PASSED",
        "tests_passed_count": 8,
        "total_tests": 8,
        "device_used": str(device),
        "details": test_results,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    logger.info("Saved Preflight Test Report to %s", out_path.name)
    logger.info("=== PREFLIGHT VERIFICATION COMPLETED SUCCESSFULLY ===")
    return summary_report


def main():
    report = run_preflight_test()
    print("\n" + "=" * 60)
    print("PREFLIGHT TEST OUTCOME")
    print("=" * 60)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
