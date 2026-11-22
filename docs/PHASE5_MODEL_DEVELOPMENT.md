# Phase 5 — First Satellite Land-Cover Model Development
### Pand Shield AI Platform

This document details the complete model architecture, spatial splitting methodology, class imbalance mitigation strategy, training pipeline, and preflight verification results for **Phase 5: First Satellite Land-Cover Model Development**.

---

## 1. Executive Summary

In Phase 5, Pand Shield AI established its first production-grade deep learning segmentation subsystem for multi-spectral/RGB satellite earth observation.
* **Architecture**: 4-level DoubleConv U-Net (`SatelliteUNet`) with skip connections and spatial dropout (7,763,239 trainable parameters).
* **Target Classes**: 7 classes (`1` through `7`). In strict adherence to scientific validation guidelines, all classes are preserved as numeric identifiers and are never mapped to unverified semantic strings.
* **Spatial Leakage Mitigation**: 20 km spatial block partitioning segregates training and validation data geographically into 97 train blocks (24,449 tiles / 80.06%) and 24 validation blocks (6,088 tiles / 19.94%) with **zero tile or block overlap**.
* **Loss Function**: `CombinedWeightedLoss` blending class-weighted Cross-Entropy (mitigating the 40.3:1 empirical class imbalance using inverse-frequency scaling) and Multiclass Dice Loss.
* **Preflight Verification**: 8-stage automated preflight test suite executed with a **100% PASS** rate.

---

## 2. Directory & Module Architecture

The machine learning subsystem is organized into modular packages under [`ml/`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml):

```text
ml/
├── __init__.py
├── README.md                          # Quickstart & CLI usage guide
├── data/
│   ├── __init__.py
│   ├── dataset.py                     # SatelliteSegmentationDataset (PyTorch Dataset)
│   ├── spatial_split.py               # SpatialSplitEngine (20 km block isolation)
│   ├── loaders/                       # PyArrow & binary decoders (Phase 4)
│   ├── preprocessing/                 # Tabular & parquet validators (Phase 4)
│   ├── validation/                    # Spatial & coordinate validation (Phase 4)
│   └── calibration/                   # Calibration strips & readiness audit (Phase 4)
├── models/
│   ├── __init__.py
│   └── unet.py                        # SatelliteUNet architecture & prediction decoder
└── training/
    ├── __init__.py
    ├── losses.py                      # MulticlassDiceLoss & CombinedWeightedLoss
    ├── metrics.py                     # SegmentationMetrics (mIoU, Dice, ConfMatrix)
    ├── trainer.py                     # SegmentationTrainer (checkpoints, early stopping)
    ├── train.py                       # Modular CLI training orchestrator
    └── preflight.py                   # 8-step automated preflight test suite
```

Generated outputs and model checkpoints are persisted in:
* [`data/processed/splits/spatial_train_val_split.json`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/splits/spatial_train_val_split.json): 20 km spatial partitioning index cache.
* [`data/processed/models/preflight_test_report.json`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/models/preflight_test_report.json): Automated preflight validation results.
* `data/processed/models/best_model.pt`: Checkpoint with highest validation mIoU (saved during training).
* `data/processed/models/latest_checkpoint.pt`: Checkpoint saved at the end of each epoch.
* `data/processed/models/training_history.json`: Structured per-epoch loss and evaluation metrics.

---

## 3. Spatial Leakage Mitigation (20 km Block Splitting)

### Spatial Autocorrelation Problem
Randomly splitting satellite imagery tiles into train and validation sets introduces severe **spatial autocorrelation leakage**. Adjacent satellite tiles (e.g., $640\text{ m} \times 640\text{ m}$) share continuous agricultural plots, urban corridors, soil signatures, and cloud covers. A model evaluated on adjacent tiles memorizes regional features, reporting artificially inflated evaluation metrics while failing on unseen geographies.

### Spatial Block Engine Formulation
[`SpatialSplitEngine`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml/data/spatial_split.py) partitions geographic space into discrete square blocks:

$$\text{Block}_X = \left\lfloor \frac{\text{Longitude} \cdot 111.32 \cdot \cos(\text{Latitude}_{\text{ref}})}{S_{\text{block}}} \right\rfloor, \quad \text{Block}_Y = \left\lfloor \frac{\text{Latitude} \cdot 110.57}{S_{\text{block}}} \right\rfloor$$

Where:
* $S_{\text{block}} = 20.0\text{ km}$
* $\text{Latitude}_{\text{ref}} = 28.5^\circ\text{ N}$ (Regional center for Delhi NCR)

### Partitioning Statistics
* **Total Samples**: 30,537 tiles
* **Total Discovered Spatial Blocks**: 121
* **Training Partition**: 97 spatial blocks $\rightarrow$ **24,449 tiles** ($80.06\%$)
* **Validation Partition**: 24 spatial blocks $\rightarrow$ **6,088 tiles** ($19.94\%$)
* **Overlapping Blocks / Tiles**: **0** ($100\%$ geographic isolation)

---

## 4. PyTorch Dataset & Data Pipeline

### Tensor Formatting and Normalization
[`SatelliteSegmentationDataset`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml/data/dataset.py) wraps the raw Parquet byte streams:
1. **RGB Image Decoding**: Decodes PNG/GeoTIFF byte stream to $64 \times 64 \times 3$ uint8.
2. **Standardization**: Converts values to float32 $\in [0.0, 1.0]$ and standardizes using Sentinel-2/ImageNet transfer coefficients:
   $$\mu = [0.485, 0.456, 0.406], \quad \sigma = [0.229, 0.224, 0.225]$$
   Transposes shape to PyTorch channel-first format: `torch.FloatTensor` of shape `[3, 64, 64]`.
3. **Mask Decoding & Class Re-indexing**:
   * Ground truth mask values range from `1` to `7`.
   * For compatibility with PyTorch zero-indexed classification losses (`nn.CrossEntropyLoss`), classes are internally mapped via $y_{\text{internal}} = y_{\text{raw}} - 1 \in [0, 6]$.
   * Shape: `torch.LongTensor` of shape `[64, 64]`.
   * Inference output is converted back to ground-truth IDs via $y_{\text{output}} = \hat{y} + 1 \in [1, 7]$.
4. **RAM Caching**:
   At $16\text{ KB}$ per uncompressed tile pair ($12\text{ KB}$ image + $4\text{ KB}$ mask), all 30,537 tiles consume only $\approx 477\text{ MB}$ of RAM. An optional `--cache-in-memory` flag preloads samples into memory for near-instantaneous epoch batching.

---

## 5. Model Architecture (`SatelliteUNet`)

[`SatelliteUNet`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml/models/unet.py) implements a symmetrical encoder-decoder network optimized for $64 \times 64$ multi-spectral patch segmentation:

```text
Input: [B, 3, 64, 64]
│
├── Encoder Stage 1: Conv2D(3->32) -> BatchNorm -> ReLU -> Conv2D(32->32) -> BatchNorm -> ReLU [Skip 1]
│   └── MaxPool2D(2x2) -> [B, 32, 32, 32]
│
├── Encoder Stage 2: Conv2D(32->64) -> BatchNorm -> ReLU -> Conv2D(64->64) -> BatchNorm -> ReLU [Skip 2]
│   └── MaxPool2D(2x2) -> [B, 64, 16, 16]
│
├── Encoder Stage 3: Conv2D(64->128) -> BatchNorm -> ReLU -> Conv2D(128->128) -> BatchNorm -> ReLU [Skip 3]
│   └── MaxPool2D(2x2) -> [B, 128, 8, 8]
│
├── Encoder Stage 4: Conv2D(128->256) -> BatchNorm -> ReLU -> Conv2D(256->256) -> BatchNorm -> ReLU [Skip 4]
│   └── MaxPool2D(2x2) -> [B, 256, 4, 4]
│
├── Bottleneck: Conv2D(256->512) -> BatchNorm -> ReLU -> Conv2D(512->512) -> BatchNorm -> ReLU
│   └── Spatial Dropout (p = 0.2)
│
├── Decoder Stage 4: ConvTranspose2D(512->256) -> Concat(Skip 4) -> DoubleConv(512->256)
├── Decoder Stage 3: ConvTranspose2D(256->128) -> Concat(Skip 3) -> DoubleConv(256->128)
├── Decoder Stage 2: ConvTranspose2D(128->64)  -> Concat(Skip 2) -> DoubleConv(128->64)
├── Decoder Stage 1: ConvTranspose2D(64->32)   -> Concat(Skip 1) -> DoubleConv(64->32)
│
└── Head: Conv2D(32 -> 7, kernel=1) -> Output Logits: [B, 7, 64, 64]
```

* **Total Parameters**: 7,763,239
* **Trainable Parameters**: 7,763,239 ($100\%$)
* **Model Size**: $\approx 29.6\text{ MB}$ (FP32)

---

## 6. Class Imbalance Mitigation & Loss Function

Phase 4 Step 4 revealed severe class distribution skew:
* Class 6: $47.74\%$ (Dominant)
* Class 5: $27.97\%$
* Class 4: $11.75\%$
* Class 3: $6.24\%$
* Class 7: $4.47\%$
* Class 2: $1.39\%$
* Class 1: $1.185\%$ (Minority)
* Imbalance Ratio: $40.3 : 1$

Standard unweighted Cross-Entropy would collapse predictions onto Class 6 and 5. [`CombinedWeightedLoss`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml/training/losses.py) implements a hybrid loss:

$$\mathcal{L}_{\text{total}} = 0.6 \cdot \mathcal{L}_{\text{WeightedCE}} + 0.4 \cdot \mathcal{L}_{\text{MultiDice}}$$

### Inverse-Frequency Cross-Entropy
Weights are calculated via smooth inverse frequency:

$$w_c = \frac{1}{\sqrt{f_c} \cdot \sum_{k=1}^7 \frac{1}{\sqrt{f_k}}}$$

| Class ID | Pixel Frequency ($f_c$) | Normal Weight ($w_c$) |
|---|---|---|
| **Class 1** | $1.185\%$ | **0.778** |
| **Class 2** | $1.390\%$ | **0.718** |
| **Class 3** | $6.240\%$ | **0.160** |
| **Class 4** | $11.750\%$ | **0.085** |
| **Class 5** | $27.970\%$ | **0.036** |
| **Class 6** | $47.740\%$ | **0.021** |
| **Class 7** | $4.470\%$ | **0.224** |

### Multiclass Soft Dice Loss
$$\mathcal{L}_{\text{MultiDice}} = 1 - \frac{1}{C} \sum_{c=0}^{C-1} \frac{2 \sum_i p_{i, c} g_{i, c} + \epsilon}{\sum_i p_{i, c}^2 + \sum_i g_{i, c}^2 + \epsilon}$$

Where $p_{i, c}$ is the softmax probability for class $c$ at pixel $i$, and $g_{i, c} \in \{0, 1\}$ is the one-hot ground-truth.

---

## 7. Evaluation Metrics & Confusion Matrix

[`SegmentationMetrics`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml/training/metrics.py) computes comprehensive spatial segmentation metrics accumulated over the complete validation partition:
1. **Overall Pixel Accuracy**: Ratio of correctly identified pixels over all pixels.
2. **Mean Intersection over Union (mIoU)**:
   $$\text{mIoU} = \frac{1}{C} \sum_{c=1}^C \frac{TP_c}{TP_c + FP_c + FN_c}$$
3. **Per-Class IoU**: Detailed breakdown across all 7 classes.
4. **Mean Dice Score**:
   $$\text{Dice}_c = \frac{2 \cdot TP_c}{2 \cdot TP_c + FP_c + FN_c}$$
5. **$7 \times 7$ Confusion Matrix**: Tracks true class row vs. predicted class column for spatial error attribution.

---

## 8. Preflight Verification Results

The automated preflight test suite was executed via:
```powershell
& ".\.venv\Scripts\python.exe" -m ml.training.preflight
```

### Results Summary
All 8 automated tests passed without warnings or regressions:

| Test ID | Verification Step | Expected Value / Behavior | Observed Result | Status |
|---|---|---|---|---|
| **Test 1** | Device Detection | Valid PyTorch device string (`cpu` or `cuda`) | `cpu` | **PASS** |
| **Test 2** | Spatial Group Split | Zero tile overlap between train and val partitions | 24,449 train / 6,088 val / **0 overlap** | **PASS** |
| **Test 3** | Sample Shapes | Image `[3, 64, 64]` float32, Mask `[64, 64]` int64 | Verified on sample `159984.png` | **PASS** |
| **Test 4** | Class ID Range | Internal target IDs strictly within $[0, 6]$ | Min: 0, Max: 6 (Maps to 1..7) | **PASS** |
| **Test 5** | Mini-Batch DataLoader | Batch tensors `[4, 3, 64, 64]` and `[4, 64, 64]` | Correct shapes and types | **PASS** |
| **Test 6** | Forward Pass | Output logits shape `[4, 7, 64, 64]` | Verified (7,763,239 params) | **PASS** |
| **Test 7** | Loss & Gradients | Finite loss scalar and valid non-null gradients | Loss = 1.4573, gradients verified | **PASS** |
| **Test 8** | Metrics Accumulation | mIoU, Dice, Pixel Acc, $7 \times 7$ Confusion Matrix | Verified | **PASS** |

Artifact: [`data/processed/models/preflight_test_report.json`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/models/preflight_test_report.json).

---

## 9. Training CLI Usage

To launch model training, use the modular training entry point [`ml/training/train.py`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml/training/train.py):

### Quick Test / Smoke Run
```powershell
& ".\.venv\Scripts\python.exe" -m ml.training.train --sample-limit 500 --epochs 2 --batch-size 16 --cache-in-memory
```

### Production Baseline Training
```powershell
& ".\.venv\Scripts\python.exe" -m ml.training.train --epochs 25 --batch-size 32 --lr 0.001 --cache-in-memory
```

### Configurable CLI Flags
* `--parquet-path`: Path to input Parquet (default: `data/raw/train-00000-of-00007.parquet`).
* `--output-dir`: Output directory for checkpoints and logs (default: `data/processed/models`).
* `--epochs`: Maximum training epochs (default: `20`).
* `--batch-size`: Batch size (default: `32`).
* `--lr`: Initial AdamW learning rate (default: `1e-3`).
* `--weight-decay`: L2 regularization coefficient (default: `1e-4`).
* `--patience`: Early stopping patience epochs on validation mIoU (default: `5`).
* `--block-size-km`: Spatial block size in kilometers (default: `20.0`).
* `--sample-limit`: Limit total samples for rapid debugging/testing (default: `None` / all 30,537).
* `--cache-in-memory`: Preload decoded tensors in RAM for maximum epoch throughput.
* `--device`: Hardware device override (`cuda` or `cpu`).
