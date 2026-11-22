"""
KSHETRA — LAND SHIELD AI
Database Management & Unified SQLite Schema.

Provides thread-safe connections and schema initialization for:
- User authentication & active sessions
- Saved land parcels & custom surveyor notes
- Environmental audit & risk reports
- Geographic points & boundary metadata (geo_locations)
- Land observations & biophysical measurements (land_observations)
- Satellite imagery acquisition metadata (imagery_metadata)
- Classical ML model registries & evaluations (ml_models, ml_evaluations, ml_predictions)
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger("kshetra.backend.database")

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "kshetra_auth.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection() -> sqlite3.Connection:
    """Returns an SQLite connection configured with Row factory."""
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes and migrates all KSHETRA database tables safely."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            organization TEXT,
            role TEXT DEFAULT 'Land Intelligence Surveyor',
            units TEXT DEFAULT 'ha',
            default_basemap TEXT DEFAULT 'satellite',
            reduced_motion INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 3. Saved Places
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_places (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            notes TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            is_demo INTEGER DEFAULT 0,
            demo_index INTEGER,
            area_ha REAL DEFAULT 40.96,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 4. Reports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            place_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            report_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 5. Geographic Locations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geo_locations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            state TEXT,
            district TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            location_type TEXT DEFAULT 'survey_region',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. Land Observations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS land_observations (
            id TEXT PRIMARY KEY,
            location_id TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            vegetation_pct REAL,
            water_pct REAL,
            built_up_pct REAL,
            soil_pct REAL,
            elevation_m REAL,
            slope_deg REAL,
            dominant_class TEXT,
            observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 7. Satellite Imagery Metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagery_metadata (
            id TEXT PRIMARY KEY,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            sensor TEXT NOT NULL,
            acquisition_date TEXT,
            resolution_m REAL,
            file_path TEXT,
            thumbnail_url TEXT,
            attribution TEXT,
            license TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 8. ML Models Registry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            target_variable TEXT,
            version TEXT DEFAULT '1.0.0',
            metrics_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 9. ML Evaluations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_evaluations (
            id TEXT PRIMARY KEY,
            model_id TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            dataset_name TEXT,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES ml_models (id) ON DELETE CASCADE
        )
    """)

    # 10. ML Predictions Audit
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_predictions (
            id TEXT PRIMARY KEY,
            model_id TEXT NOT NULL,
            input_features TEXT NOT NULL,
            prediction_result TEXT NOT NULL,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed demo user if not present
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, email, full_name, password_hash, salt, organization, role)
        VALUES ('demo_user', 'demo@kshetra.ai', 'Guest Surveyor', 'none', 'none', 'Independent Surveyor', 'Field Surveyor')
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized with 10 tables at %s", DB_PATH)


def seed_ml_models_registry():
    """Populates the ml_models and ml_evaluations tables from ml_models_registry.json."""
    registry_file = BASE_DIR / "data" / "processed" / "classical" / "ml_models_registry.json"
    if not registry_file.is_file():
        return

    try:
        with open(registry_file, "r") as f:
            data = json.load(f)

        conn = get_db_connection()
        cursor = conn.cursor()

        for model_id, model_info in data.get("models", {}).items():
            cursor.execute("""
                INSERT OR REPLACE INTO ml_models (id, name, category, target_variable, version, metrics_json)
                VALUES (?, ?, ?, ?, '1.0.0', ?)
            """, (
                model_id,
                model_info.get("name"),
                model_info.get("syllabus_category"),
                model_info.get("target", "N/A"),
                json.dumps(model_info.get("metrics", {}))
            ))

            for metric_k, metric_v in model_info.get("metrics", {}).items():
                if isinstance(metric_v, (int, float)):
                    cursor.execute("""
                        INSERT OR REPLACE INTO ml_evaluations (id, model_id, metric_name, metric_value, dataset_name)
                        VALUES (?, ?, ?, ?, 'Sentinel-2 Harmonized Test')
                    """, (f"{model_id}_{metric_k}", model_id, metric_k, float(metric_v)))

        conn.commit()
        conn.close()
        logger.info("Seeded ML models registry and evaluations into SQLite")
    except Exception as e:
        logger.warning("Failed to seed ML models registry: %s", e)


if __name__ == "__main__":
    init_database()
    seed_ml_models_registry()
    print("Database initialization and ML models seeding complete.")
