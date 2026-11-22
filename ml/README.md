# Machine Learning Subsystem — Land Shield AI

This directory contains the machine learning and deep learning pipelines for satellite Earth observation and land-cover segmentation.

---

## Directory Structure

```text
ml/
├── data/
│   ├── dataset.py            # PyTorch Dataset for satellite tiles & mask decoding
│   ├── spatial_split.py      # SpatialSplitEngine (20km block isolation)
│   ├── loaders/              # PyArrow streaming reader and image decoders
│   ├── preprocessing/        # Data validation and point harmonizer
│   ├── validation/           # Haversine spatial discrepancy validator
│   └── calibration/          # Spectral analysis and visual calibration
├── models/
│   └── unet.py               # SatelliteUNet architecture (7 classes, skip connections)
└── training/
    ├── losses.py             # CombinedWeightedLoss (Weighted CE + Soft Dice)
    ├── metrics.py            # SegmentationMetrics (mIoU, Dice, Pixel Acc, ConfMatrix)
    ├── trainer.py            # SegmentationTrainer (early stopping, checkpoint saving)
    ├── train.py              # CLI entry point for model training
    └── preflight.py          # 8-step preflight verification test suite
```

---

## Quickstart

### 1. Run Preflight Test Suite
Verify your environment, tensor shapes, gradient flow, and spatial split integrity before training:
```powershell
& ".\.venv\Scripts\python.exe" -m ml.training.preflight
```

### 2. Run Smoke / Debug Training Run
Train for 2 epochs on 500 samples with in-memory caching:
```powershell
& ".\.venv\Scripts\python.exe" -m ml.training.train --sample-limit 500 --epochs 2 --batch-size 16 --cache-in-memory
```

### 3. Launch Full Production Baseline Training
```powershell
& ".\.venv\Scripts\python.exe" -m ml.training.train --epochs 25 --batch-size 32 --lr 0.001 --cache-in-memory
```

Checkpoints will be written to `data/processed/models/best_model.pt` and `latest_checkpoint.pt`.
Evaluation logs will be recorded in `data/processed/models/training_history.json`.

For in-depth architectural and mathematical documentation, see [`docs/PHASE5_MODEL_DEVELOPMENT.md`](../docs/PHASE5_MODEL_DEVELOPMENT.md).
