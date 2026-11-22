# Phase 4 — Data Engineering & Preprocessing Foundation
### Pand Shield AI Platform

This document details the complete data engineering architecture, harmonization logic, label verification policies, and validation test results across **Phase 4 (Steps 1, 2, and 3)**.

---

## 1. Directory & Code Architecture

The data engineering subsystem is located under [`ml/data/`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/ml/data) and produces versioned outputs in [`data/processed/`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed):

```text
ml/data/
├── __init__.py
├── loaders/
│   ├── __init__.py
│   └── parquet_loader.py            # Streaming PyArrow reader & binary decoders
├── preprocessing/
│   ├── __init__.py
│   ├── dataset_inspector.py         # Memory-conscious tabular & parquet auditor
│   ├── point_harmonizer.py          # Coordinate-precision multi-temporal joiner
│   ├── parquet_validator.py         # Parquet streaming validator & label verifier
│   └── pipeline.py                  # End-to-end reproducible pipeline orchestrator
└── validation/
    ├── __init__.py
    └── coordinate_validator.py      # Spatial discrepancy & Haversine detector
```

---

## 2. Harmonization Methodology & Schema Normalization

### Rationale & Rules
1. **Preserve Coordinate Precision**: Never round coordinates for matching. Floating-point numbers are read and matched using 64-bit precision.
2. **Coordinate-First Joins**: The export identifier `system:index` in `TrainingPoints2016.csv` is compromised (rows 224–233 were corrupted to `"0.00E+00"` by spreadsheet software). Therefore, joins are performed strictly on geographical coordinates.
3. **Zero Unexplained Record Loss**:
   * Total input in 2016: 968 points.
   * Total input in 2024: 968 points.
   * Total harmonized output: **968 records** ($100\%$ retention rate).

### Harmonization Results
* **Exact Raw Matches**: **967** points share identical float64 coordinates between 2016 and 2024.
* **Spatial Proximity Match (Micro-shift)**: Exactly **1 point** has a geographic drift of **$8.1553\text{ meters}$** (smaller than 1 Sentinel-2 pixel):
  * 2016: `(76.87743144028781, 30.68311561903436)` (Class 0)
  * 2024: `(76.87738335535985, 30.68317619199697)` (Class 0)
  * Both coordinates are preserved in `longitude_2016`, `latitude_2016`, `longitude_2024`, and `latitude_2024`, with `spatial_drift_meters=8.1553` explicitly recorded.
* **Transition Statistics**:
  * `0_to_0` (Stable Class 0): **512** points ($52.89\%$)
  * `0_to_2` (Converted Class 0 $\rightarrow$ 2): **267** points ($27.58\%$)
  * `1_to_1` (Stable Class 1): **189** points ($19.52\%$)
  * Total stable points: **701** ($72.42\%$) | Converted points: **267** ($27.58\%$).

---

## 3. Label Verification Policy (Zero-Fabrication Standard)

* **Parquet Dataset (`train-00000-of-00007.parquet`)**:
  * Semantic masks store integer IDs: `1, 2, 3, 4, 5, 6, 7`.
  * **Verified Finding**: No string class legend is embedded in the GeoTIFF headers or Parquet metadata.
  * **Policy**: To avoid fabricating labels, class semantics are documented strictly as `CLASS_1` through `CLASS_7` with empirical pixel frequencies. Semantic assignment is designated as `AWAITING_GROUND_TRUTH_CALIBRATION`.
* **Empirical Class Frequencies (Audited Sample of 2,048,000 Pixels)**:
  * `Class 1`: 24,265 px ($1.185\%$)
  * `Class 2`: 26,482 px ($1.293\%$)
  * `Class 3`: 125,668 px ($6.136\%$)
  * `Class 4`: 239,649 px ($11.702\%$)
  * `Class 5`: 564,824 px ($27.579\%$)
  * `Class 6`: 977,757 px ($47.742\%$)
  * `Class 7`: 89,355 px ($4.363\%$)

---

## 4. Generated Artifacts in `data/processed/`

| File Name | Format | Size | Description |
| :--- | :---: | :---: | :--- |
| [`harmonized_points_2016_2024.parquet`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/harmonized_points_2016_2024.parquet) | Parquet | ~80.7 KB | Standardized, typed ground truth table with transitions |
| [`harmonized_points_2016_2024.csv`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/harmonized_points_2016_2024.csv) | CSV | ~192.4 KB | Human-readable version of the harmonized points table |
| [`data_quality_report.json`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/data_quality_report.json) | JSON | ~1.3 KB | Quality audit, null counts, anomalies, and retention rates |
| [`preprocessing_summary.json`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/preprocessing_summary.json) | JSON | ~1.5 KB | Executive summary of pipeline execution and metrics |
| [`unmatched_or_drift_records.json`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/unmatched_or_drift_records.json) | JSON | ~395 B | Log of coordinate drift record (PT_0968; 8.16m shift) |
| [`label_mapping_documentation.json`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/processed/label_mapping_documentation.json) | JSON | ~1.8 KB | Factual pixel counts, frequencies, and calibration status |

---

## 5. Execution & Reproducibility Command

To rerun the complete data engineering and preprocessing pipeline:

```powershell
& ".\.venv\Scripts\python.exe" -m ml.data.preprocessing.pipeline
```

---

## 6. Raw Data Integrity Confirmation

The directory [`data/raw/`](file:///c:/Users/DAKSH/Desktop/land%20shield%20ai/data/raw) remains strictly read-only:
* `train-00000-of-00007.parquet` (442,520,270 bytes) — Untouched
* `TrainingPoints2016.csv` (90,943 bytes) — Untouched
* `TrainingPoints2024.csv` (85,559 bytes) — Untouched
* `inspect_data.py` (897 bytes) — Untouched
