"""
step3_layers.py — Render layer PNGs and write layers.json.

Reads:
  data/processed/slope.npy         — float32 slope array from step2
  data/raw/cropped_dtm.tif         — cropped DTM from step1 (for hillshade + extent)

Writes:
  data/processed/layers/slope.png      — 8-bit grayscale slope image
  data/processed/layers/hillshade.png  — 8-bit grayscale hillshade image
  data/processed/layers/layers.json    — layer manifest (REQ-06)

Usage:
    .venv/Scripts/python.exe pipeline/step3_layers.py
"""

import json
import sys
from math import cos, sin
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

slope_npy_path   = REPO_ROOT / "data" / "processed" / "slope.npy"
cropped_dtm_path = REPO_ROOT / config["cropped_dtm"]
layers_dir       = REPO_ROOT / "data" / "processed" / "layers"
slope_png_path   = layers_dir / "slope.png"
hillshade_png_path = layers_dir / "hillshade.png"
layers_json_path = layers_dir / "layers.json"

# ---------------------------------------------------------------------------
# Input existence checks
# ---------------------------------------------------------------------------
if not slope_npy_path.exists():
    print(
        f"Error: slope array not found at:\n  {slope_npy_path}\n"
        "Run step2_slope.py first to produce the slope data."
    )
    sys.exit(1)

if not cropped_dtm_path.exists():
    print(
        f"Error: cropped DTM not found at:\n  {cropped_dtm_path}\n"
        "Run step1_crop_dtm.py first to produce the cropped intermediate file."
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Imports (after existence checks for clean error messages)
# ---------------------------------------------------------------------------
import rasterio          # noqa: E402
import rasterio.warp     # noqa: E402
from PIL import Image    # noqa: E402

# ---------------------------------------------------------------------------
# Create output directory
# ---------------------------------------------------------------------------
layers_dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 3a — Slope PNG
# ---------------------------------------------------------------------------
slope = np.load(slope_npy_path)

max_deg = float(config.get("slope_colormap_max_deg", 45))

# Normalise to [0, 255]; NaN pixels clamp to 0
slope_clipped = np.where(np.isnan(slope), 0.0, slope)
slope_norm = np.clip(slope_clipped / max_deg, 0.0, 1.0)
slope_uint8 = (slope_norm * 255).astype(np.uint8)

Image.fromarray(slope_uint8, mode="L").save(slope_png_path)

# ---------------------------------------------------------------------------
# 3b — Hillshade PNG
# ---------------------------------------------------------------------------
AZIMUTH  = 315.0   # degrees, standard illumination from NW
ALTITUDE = 45.0    # degrees above horizon

with rasterio.open(cropped_dtm_path) as ds:
    elev = ds.read(1).astype(np.float32)

    if ds.nodata is not None:
        elev[elev == ds.nodata] = np.nan

    dx = abs(ds.transform.a)   # pixel size in metres

    src_crs = ds.crs
    # Four corners in native projected CRS (col, row order):
    #   (tl_x, tl_y) = top-left,  (br_x, br_y) = bottom-right
    tl_x = ds.transform.c          # west edge
    tl_y = ds.transform.f          # north edge
    br_x = tl_x + ds.width  * dx  # east edge
    br_y = tl_y - ds.height * dx  # south edge (transform.e is negative)

# Compute hillshade using the standard formula:
#   hillshade = cos(zenith) · cos(slope) + sin(zenith) · sin(slope) · cos(azimuth - aspect)
dz_dy, dz_dx = np.gradient(elev, dx, dx)

slope_rad  = np.arctan(np.sqrt(dz_dx ** 2 + dz_dy ** 2))
aspect_rad = np.arctan2(dz_dy, dz_dx)   # geographic aspect

zenith_rad  = np.radians(90.0 - ALTITUDE)
# Illumination azimuth in math convention (measured from east, counter-clockwise)
azimuth_rad = np.radians(360.0 - AZIMUTH + 90.0)

hs = (
    cos(zenith_rad) * np.cos(slope_rad)
    + sin(zenith_rad) * np.sin(slope_rad) * np.cos(azimuth_rad - aspect_rad)
)

# Clamp and scale; NaN → 0
hs = np.where(np.isnan(hs), 0.0, hs)
hs = np.clip(hs, 0.0, 1.0)
hillshade_uint8 = (hs * 255).astype(np.uint8)

Image.fromarray(hillshade_uint8, mode="L").save(hillshade_png_path)

# ---------------------------------------------------------------------------
# 3c — Extent reprojection and layers.json
# ---------------------------------------------------------------------------
GEO_CRS_PRIMARY  = "EPSG:49900"
GEO_CRS_FALLBACK = "+proj=longlat +a=3396190 +b=3376200 +no_defs"

def _reproject_corners(xs, ys, src_crs, dst_crs: str):
    """Reproject a list of (x, y) pairs and return (lons, lats)."""
    lons, lats = rasterio.warp.transform(src_crs, dst_crs, xs, ys)
    return [float(v) for v in lons], [float(v) for v in lats]

# Corner coordinates in native CRS (all four corners)
corner_xs = [tl_x, br_x, tl_x, br_x]
corner_ys = [tl_y, tl_y, br_y, br_y]

try:
    lons, lats = _reproject_corners(corner_xs, corner_ys, src_crs, GEO_CRS_PRIMARY)
except Exception:
    lons, lats = _reproject_corners(corner_xs, corner_ys, src_crs, GEO_CRS_FALLBACK)

extent = {
    "west":  min(lons),
    "east":  max(lons),
    "south": min(lats),
    "north": max(lats),
}

layers = [
    {
        "name":         "Slope",
        "file":         "layers/slope.png",
        "extent":       extent,
        "data_card_id": "hirise_dtm_006",
    },
    {
        "name":         "Hillshade",
        "file":         "layers/hillshade.png",
        "extent":       extent,
        "data_card_id": "hirise_dtm_006",
    },
]

with open(layers_json_path, "w") as f:
    json.dump(layers, f, indent=2)

# ---------------------------------------------------------------------------
# Print results (REQ-07)
# ---------------------------------------------------------------------------
for path in (slope_png_path, hillshade_png_path, layers_json_path):
    print(f"{path}  {path.stat().st_size}")
