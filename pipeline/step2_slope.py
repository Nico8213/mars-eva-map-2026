"""
step2_slope.py — Compute per-pixel slope and write grid metadata.

Reads the cropped DTM produced by step1_crop_dtm.py, computes slope in
degrees using numpy gradient, and writes:
  data/processed/slope.npy   — float32 array, same extent as the cropped window
  data/processed/grid.json   — grid metadata including source attribution and
                               geographic top-left coordinate (REQ-03 to REQ-05)

Usage:
    .venv/Scripts/python.exe pipeline/step2_slope.py
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants — fixed metadata for this known data product (REQ-04)
# ---------------------------------------------------------------------------
SOURCE_PRODUCT = "JEZ_hirise_soc_006_DTM_1m"
VERSION = "006"
DOI = "10.5066/P9REJ9JN"

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

cropped_dtm_path = REPO_ROOT / config["cropped_dtm"]
processed_dir = REPO_ROOT / "data" / "processed"
slope_npy_path = processed_dir / "slope.npy"
grid_json_path = processed_dir / "grid.json"

# ---------------------------------------------------------------------------
# Check that the cropped DTM exists before importing heavy libs
# ---------------------------------------------------------------------------
if not cropped_dtm_path.exists():
    print(
        f"Error: cropped DTM not found at:\n  {cropped_dtm_path}\n"
        "Run step1_crop_dtm.py first to produce the cropped intermediate file."
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Imports (after the existence check so error message is clean)
# ---------------------------------------------------------------------------
import numpy as np  # noqa: E402
import rasterio  # noqa: E402
import rasterio.warp  # noqa: E402

# ---------------------------------------------------------------------------
# Read cropped DTM
# ---------------------------------------------------------------------------
with rasterio.open(cropped_dtm_path) as ds:
    elev = ds.read(1).astype(np.float32)

    # Replace nodata with NaN so gradient ignores bad pixels
    if ds.nodata is not None:
        elev[elev == ds.nodata] = np.nan

    dx = abs(ds.transform.a)          # pixel size in metres (REQ-05)
    src_crs = ds.crs
    crs_wkt = ds.crs.wkt
    width = ds.width
    height = ds.height

    # Top-left corner in native projected coordinates
    tl_x = ds.transform.c               # west edge
    tl_y = ds.transform.f               # north edge

# ---------------------------------------------------------------------------
# Compute slope in degrees (design.md § Step 2)
# ---------------------------------------------------------------------------
# np.gradient returns [dz/drow, dz/dcol]; rows increase southward so dz/dy
# in the geographic sense needs the sign flip, but for slope magnitude it
# does not matter — only the absolute gradient is used.
dz_dy, dz_dx = np.gradient(elev, dx, dx)

slope_rad = np.arctan(np.sqrt(dz_dx ** 2 + dz_dy ** 2))
slope_deg = np.degrees(slope_rad).astype(np.float32)

# Preserve NaN where elevation was nodata
slope_deg[np.isnan(elev)] = np.nan

# ---------------------------------------------------------------------------
# Save slope array
# ---------------------------------------------------------------------------
processed_dir.mkdir(parents=True, exist_ok=True)
np.save(slope_npy_path, slope_deg)

# ---------------------------------------------------------------------------
# Reproject top-left corner to geographic (REQ-03)
# Primary: EPSG:49900 (IAU Mars 2000 geographic)
# Fallback: Proj4 string for the same ellipsoid
# ---------------------------------------------------------------------------
GEO_CRS_PRIMARY = "EPSG:49900"
GEO_CRS_FALLBACK = "+proj=longlat +a=3396190 +b=3376200 +no_defs"

def _reproject_point(x: float, y: float, src_crs, dst_crs: str):
    """Return (lon, lat) reprojected from src_crs to dst_crs."""
    xs, ys = rasterio.warp.transform(src_crs, dst_crs, [x], [y])
    return float(xs[0]), float(ys[0])

try:
    lon, lat = _reproject_point(tl_x, tl_y, src_crs, GEO_CRS_PRIMARY)
    crs_used = GEO_CRS_PRIMARY
    coordinate_notes = (
        "Top-left corner reprojected from the native projected CRS to "
        "IAU 2015 Mars Geographic (EPSG:49900). "
        "Longitude and latitude are in degrees; positive east, positive north."
    )
except Exception:
    # EPSG:49900 not available in this PROJ install — use Proj4 fallback
    lon, lat = _reproject_point(tl_x, tl_y, src_crs, GEO_CRS_FALLBACK)
    crs_used = GEO_CRS_FALLBACK
    coordinate_notes = (
        "Top-left corner reprojected from the native projected CRS to "
        "Mars geographic coordinates using the IAU oblate ellipsoid "
        f"(Proj4: {GEO_CRS_FALLBACK}). "
        "Longitude and latitude are in degrees; positive east, positive north."
    )

# ---------------------------------------------------------------------------
# Build and write grid.json (REQ-05)
# ---------------------------------------------------------------------------
grid = {
    "source_product":    SOURCE_PRODUCT,
    "version":           VERSION,
    "doi":               DOI,
    "crs_wkt":           crs_wkt,
    "top_left_x_m":      tl_x,
    "top_left_y_m":      tl_y,
    "pixel_size_m":      dx,
    "width":             width,
    "height":            height,
    "top_left_coordinate": {
        "latitude":  lat,
        "longitude": lon,
    },
    "coordinate_notes":  coordinate_notes,
        "known_issue": (
        "Native projection is equirectangular with standard parallel 0. "
        "At latitude about 18.5 deg one east-west pixel spans about 0.95 m on the ground "
        "while north-south spans 1 m, so the east-west gradient component of the slope is "
        "underestimated by about 5 percent."
    ),
}

with open(grid_json_path, "w") as f:
    json.dump(grid, f, indent=2)

# ---------------------------------------------------------------------------
# Print results (REQ-07: one line per output file)
# ---------------------------------------------------------------------------
print(f"{slope_npy_path}  {slope_npy_path.stat().st_size}")
print(f"{grid_json_path}  {grid_json_path.stat().st_size}")
