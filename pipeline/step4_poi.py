"""
step4_poi.py — Convert manual POI pixel positions to GeoJSON (lon/lat degrees).

Reads:
  pipeline/poi_manual.csv                  — id,name,type,pixel_x,pixel_y,source,evidence
  data/processed/grid.json                 — top-left, pixel size, size, crs_wkt
  data/processed/layers/layers.json        — extent used for range check

Writes:
  data/processed/poi.geojson

Usage:
    .venv/Scripts/python.exe pipeline/step4_poi.py
"""

import csv
import json
import sys
from pathlib import Path

import rasterio.warp
from rasterio.crs import CRS

REPO_ROOT = Path(__file__).parent.parent
csv_path     = Path(__file__).parent / "poi_manual.csv"
grid_path    = REPO_ROOT / "data" / "processed" / "grid.json"
layers_path  = REPO_ROOT / "data" / "processed" / "layers" / "layers.json"
out_path     = REPO_ROOT / "data" / "processed" / "poi.geojson"

# Same geographic CRS choice as step3_layers.py
GEO_CRS_PRIMARY  = "EPSG:49900"
GEO_CRS_FALLBACK = "+proj=longlat +a=3396190 +b=3376200 +no_defs"

ALLOWED_SOURCES = {"CRISM", "optical"}
REQUIRED_COLS = ["id", "name", "type", "pixel_x", "pixel_y", "source", "evidence"]


def fail(msg):
    print(f"Error: {msg}")
    sys.exit(1)


for p in (csv_path, grid_path, layers_path):
    if not p.exists():
        fail(f"input not found: {p}")

with open(grid_path, encoding="utf-8") as f:
    grid = json.load(f)
with open(layers_path, encoding="utf-8") as f:
    layers = json.load(f)

try:
    tl_x   = float(grid["top_left_x_m"])
    tl_y   = float(grid["top_left_y_m"])
    px_m   = float(grid["pixel_size_m"])
    width  = int(grid["width"])
    height = int(grid["height"])
    crs_wkt = grid["crs_wkt"]
except KeyError as e:
    fail(f"grid.json missing field {e}")

if not layers:
    fail("layers.json is empty")
ext = layers[0]["extent"]

src_crs = CRS.from_wkt(crs_wkt)

# ---------------------------------------------------------------------------
# Read and validate CSV rows
# ---------------------------------------------------------------------------
with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
    if missing:
        fail(f"CSV missing columns: {missing}")
    rows = list(reader)

if not rows:
    fail("CSV has no data rows")

seen_ids = set()
for r in rows:
    pid = r["id"]
    if pid in seen_ids:
        fail(f"duplicate id: {pid}")
    seen_ids.add(pid)

    if r["source"] not in ALLOWED_SOURCES:
        fail(f"{pid}: source '{r['source']}' not in {sorted(ALLOWED_SOURCES)}")

    try:
        r["_px"] = int(r["pixel_x"])
        r["_py"] = int(r["pixel_y"])
    except ValueError:
        fail(f"{pid}: pixel_x/pixel_y must be integers")

    if not (0 <= r["_px"] <= width - 1):
        fail(f"{pid}: pixel_x {r['_px']} outside 0..{width - 1}")
    if not (0 <= r["_py"] <= height - 1):
        fail(f"{pid}: pixel_y {r['_py']} outside 0..{height - 1}")

# ---------------------------------------------------------------------------
# Pixel centre -> projected -> lon/lat
# ---------------------------------------------------------------------------
eastings  = [tl_x + (r["_px"] + 0.5) * px_m for r in rows]
northings = [tl_y - (r["_py"] + 0.5) * px_m for r in rows]

try:
    lons, lats = rasterio.warp.transform(src_crs, GEO_CRS_PRIMARY, eastings, northings)
except Exception:
    lons, lats = rasterio.warp.transform(src_crs, GEO_CRS_FALLBACK, eastings, northings)

# ---------------------------------------------------------------------------
# Extent check
# ---------------------------------------------------------------------------
for r, lon, lat in zip(rows, lons, lats):
    if not (ext["west"] <= lon <= ext["east"] and ext["south"] <= lat <= ext["north"]):
        fail(
            f"{r['id']}: lon/lat ({lon}, {lat}) outside layers.json extent "
            f"W{ext['west']} E{ext['east']} S{ext['south']} N{ext['north']}"
        )

# ---------------------------------------------------------------------------
# Write GeoJSON
# ---------------------------------------------------------------------------
features = [
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "properties": {
            "id": r["id"],
            "name": r["name"],
            "type": r["type"],
            "source": r["source"],
            "evidence": r["evidence"],
        },
    }
    for r, lon, lat in zip(rows, lons, lats)
]

out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"type": "FeatureCollection", "features": features}, f, indent=2, ensure_ascii=False)

for r, lon, lat in zip(rows, lons, lats):
    print(f"{r['id']}  lon={lon:.8f}  lat={lat:.8f}")
print(f"{out_path}  {out_path.stat().st_size}")
