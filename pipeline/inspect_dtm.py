"""
inspect_dtm.py — Print metadata from the source DTM GeoTIFF without loading pixel data.

Usage:
    .venv/Scripts/python.exe pipeline/inspect_dtm.py
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

source_path = REPO_ROOT / config["source_dtm"]

# ---------------------------------------------------------------------------
# Check existence before importing rasterio (faster failure message)
# ---------------------------------------------------------------------------
if not source_path.exists():
    print(f"Error: source DTM not found at:\n  {source_path}")
    print()
    print("Steps to fix:")
    print("  1. Place the file at that location, or")
    print('  2. Update "source_dtm" in pipeline/config.json to the correct path.')
    sys.exit(1)

# ---------------------------------------------------------------------------
# Open and inspect
# ---------------------------------------------------------------------------
import rasterio  # noqa: E402  (imported after path check)

with rasterio.open(source_path) as ds:
    file_size = source_path.stat().st_size
    bounds = ds.bounds
    t = ds.transform

    try:
        proj4 = ds.crs.to_proj4()
    except Exception:
        proj4 = "(unavailable)"

    try:
        wkt = ds.crs.to_wkt()
    except Exception:
        wkt = "(unavailable)"

    nodata = ds.nodata
    dtype = ds.dtypes[0]

print("=" * 60)
print("Source DTM inspection")
print("=" * 60)
print(f"Path       : {source_path}")
print(f"Size       : {file_size:,} bytes  ({file_size / 1_048_576:.1f} MB)")
print()
print(f"Dimensions : {ds.width} px wide × {ds.height} px tall")
print(f"Band dtype : {dtype}")
print(f"Nodata     : {nodata}")
print()
print("Affine transform (native projected CRS):")
print(f"  | {t.a:>14.4f}  {t.b:>14.4f}  {t.c:>14.4f} |")
print(f"  | {t.d:>14.4f}  {t.e:>14.4f}  {t.f:>14.4f} |")
print()
print("Bounding box (native projected CRS, metres):")
print(f"  west  : {bounds.left:.4f}")
print(f"  east  : {bounds.right:.4f}")
print(f"  south : {bounds.bottom:.4f}")
print(f"  north : {bounds.top:.4f}")
print()
print("CRS (PROJ4):")
print(f"  {proj4}")
print()
print("CRS (WKT):")
for line in wkt.splitlines():
    print(f"  {line}")
print("=" * 60)
