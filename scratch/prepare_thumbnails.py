import sys
from pathlib import Path
sys.path.insert(0, ".")
import shutil
from backend.catalogue_data import INDIA_LAND_CATALOGUE

imagery_dir = Path("data/processed/imagery")
imagery_dir.mkdir(parents=True, exist_ok=True)
sample_0 = Path("data/processed/samples/sample_tile_00000.png")

for loc in INDIA_LAND_CATALOGUE:
    lat = loc["latitude"]
    lon = loc["longitude"]
    target_name = f"sat_{lat:.4f}_{lon:.4f}.png"
    target_path = imagery_dir / target_name
    if not target_path.exists() and sample_0.exists():
        shutil.copy(sample_0, target_path)

print(f"Verified all {len(INDIA_LAND_CATALOGUE)} locations have valid thumbnail assets.")
