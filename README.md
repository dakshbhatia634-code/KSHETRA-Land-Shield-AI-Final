# Land Shield AI
### *The Enterprise AI-Powered Geospatial Land Intelligence Platform*

Land Shield AI is an enterprise-grade geospatial intelligence and land evaluation platform designed to provide rapid, reliable, and actionable insights for any parcel of land. Powered by deep learning (`SatelliteUNet` with CUDA acceleration), Sentinel-2 optical Earth observation imagery, and spatial telemetry, Land Shield AI enables real-time 7-class land-cover semantic segmentation and land intelligence auditing.

---

## 🌟 Core Product Features

1. **High-Resolution Satellite Land-Cover Segmentation**:
   - Deep-learning based 7-class semantic segmentation using `SatelliteUNet` (7.76M parameters).
   - Trained on 30,537 Sentinel-2 10m GSD satellite tiles (Delhi NCR & surrounding regional mosaic).
   - Validated model checkpoint achieving **0.4839 val mIoU** and **79.59% accuracy**.
   - Ultra-fast CUDA acceleration (~6ms inference per 640m×640m tile on NVIDIA RTX 3050).

2. **Interactive Geospatial Dashboard**:
   - Dark-themed MapLibre GL interface with dual-mode basemaps (CartoDB Dark Matter & Esri World Imagery).
   - Verified Sentinel-2 sample pins with exact WGS84 coordinates derived from GeoTIFF tiepoints.
   - 1-click sample analysis and custom satellite image drag-and-drop upload.

3. **Multi-View Image & Segmentation Blending**:
   - Interactive alpha blend slider (0–100%) for smooth transitions between original satellite RGB and colorized semantic masks.
   - Multi-view switching: Interactive Blend, 3-Panel Composite, Full Colorized Mask, Raw RGB.
   - Complete color legend and spectral proxy mappings.

4. **Comprehensive Land Intelligence Report**:
   - Total analyzed area (40.96 ha standard tile footprint at 10m/px GSD).
   - 7-class breakdown with exact pixel counts, percentages, and calculated land coverage in hectares.
   - Spectral proxies: Vegetation Canopy, Built-up Structures, Water/Moisture, Bare Soil.
   - Mean softmax prediction confidence score.
   - Official Land Intelligence Audit Dossier modal with 1-click printable view and structured JSON export.

---

## 🛡️ Core Guiding Principles

* **Data Integrity Over Guesswork**: We never fabricate ownership, legal titles, or cadastral boundaries.
* **Strict Provenance Labeling**:
  - `[VERIFIED]` — Authoritative sensor metadata and WGS84 GeoTIFF tiepoints.
  - `[PREDICTED]` — Deep learning model inference with softmax confidence.
  - `[UNAVAILABLE / NOT IN DATASET]` — Cadastral ownership, legal titles, and chemical soil fertility are explicitly marked as unavailable.
* **Production-Grade Reliability**: Robust error handling, validation, and sub-10ms neural network inference.

---

## 🚀 Quickstart & Execution

### 1. Launch Backend & Frontend Server
```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 2. Access Web Platform
Open your browser to:
**`http://127.0.0.1:8000`**

- Interactive Swagger API docs: `http://127.0.0.1:8000/docs`
- Health check telemetry: `http://127.0.0.1:8000/api/health`

---

## 📁 Repository Structure

```text
land shield ai/
├── backend/                 # FastAPI REST API & routes
│   ├── config.py            # System configuration & spatial constants
│   ├── main.py              # Application entrypoint & static mounts
│   ├── schemas.py           # Pydantic telemetry & response models
│   └── routes/              # Health & prediction endpoints
├── frontend/                # Enterprise web dashboard
│   └── index.html           # MapLibre GL single-page application
├── ml/                      # Machine Learning Subsystem
│   ├── models/unet.py       # SatelliteUNet architecture
│   ├── inference/           # Real-time predictor & CLI tools
│   └── training/            # Training pipeline, losses & metrics
├── data/
│   ├── raw/                 # Original Sentinel-2 dataset (Read-Only)
│   └── processed/           # Checkpoints, sample tiles & manifests
└── tests/                   # End-to-end verification test suite
```

---

## 📁 Repository Structure

```text
land shield ai/
├── data/
│   ├── raw/                 # Original ground truth datasets (Read-Only)
│   │   ├── train-00000-of-00007.parquet  # Sentinel-2 10m image-mask pairs
│   │   ├── TrainingPoints2016.csv        # 2016 GEE ground truth points (India)
│   │   ├── TrainingPoints2024.csv        # 2024 GEE ground truth points (India)
│   │   └── inspect_data.py               # Dataset diagnostic script
│   └── processed/           # Cached tiles, preprocessed tensors, clean tables
│
├── ml/                      # Machine Learning & Computer Vision engine
│   ├── data/                # Dataset loaders, augmentations, and split generators
│   ├── models/              # Architecture definitions (U-Net, SegFormer, etc.)
│   ├── training/            # Training scripts, loss functions, evaluation metrics
│   └── inference/           # Fast model serving, ONNX/TorchScript pipelines
│
├── services/                # External Geospatial & Data Integration Connectors
│   │                        # (SoilGrids, Open-Meteo, Copernicus DEM, Cadastral)
│
├── backend/                 # Core REST/GraphQL API & business logic layer
├── frontend/                # Interactive geospatial map UI & reporting dashboard
├── docs/                    # Architecture diagrams, API specs, and research logs
├── .gitignore               # Strict exclusion of caches, venvs, and model weights
└── README.md                # Project documentation and roadmap
```

---

## 🛰️ Dataset Registry & Provenance

* **`train-00000-of-00007.parquet`**:
  * **Volume**: 30,537 image-mask pairs (Shard 0 of 7; 422 MB).
  * **Imagery**: 64×64 pixel optical satellite tiles (PNG).
  * **Masks**: 64×64 pixel GeoTIFF semantic masks with 7 distinct land cover classes.
  * **Spatial Reference**: UTM Zone 43N (Delhi-NCR, Haryana, Rajasthan, Western UP).
  * **Resolution**: 10 meters per pixel ($640\text{ m} \times 640\text{ m}$ ground footprint).

* **`TrainingPoints2016.csv` & `TrainingPoints2024.csv`**:
  * **Volume**: 968 aligned coordinate pairs across India.
  * **Coordinate Range**: Lon: 68.94°E – 96.78°E, Lat: 8.48°N – 32.54°N.
  * **Classes**: Binary & multi-class land cover states.
  * **Significance**: Enables 8-year longitudinal Land Use / Land Cover (LULC) change analysis and urbanization dynamics.

---

## 🗺️ Project Roadmap

- [x] **Phase 1: Project Foundation & Scalable Architecture**
  - Workspace inspection, dataset integrity validation, and professional directory layout.
- [ ] **Phase 2: Environment Configuration & Dependencies**
  - Dedicated virtual environment setup, pinning core geospatial and ML packages.
- [ ] **Phase 3: Machine Learning & Vision Pipeline**
  - Data loaders for Parquet shards, semantic segmentation model training, and tile inference.
- [ ] **Phase 4: Real-Time Geospatial & Environmental Services**
  - Integration with SoilGrids, Open-Meteo, and Copernicus Elevation services.
- [ ] **Phase 5: Backend API & AI Synthesis Engine**
  - FastAPI-based microservices aggregating spatial queries into structured JSON dossiers.
- [ ] **Phase 6: Interactive Geospatial Frontend**
  - Mapbox / Leaflet parcel selection canvas with real-time intelligence report visualization.

---

## 📄 License & Confidentiality
Proprietary land intelligence software architecture. All rights reserved.
"# KSHETRA-Land-Shield-AI" 
