"""
step1_crop_dtm.py — Windowed-read crop of the source HiRISE DTM.

Reads the area of interest from pipeline/config.json, extracts that
sub-window from the source GeoTIFF using rasterio windowed reads
(the full file is never loaded into memory), and writes the cropped
raster to data/raw/cropped_dtm.tif.

Usage:
    .venv/Scripts/python.exe pipeline/step1_crop_dtm.py
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

# ---------------------------------------------------------------------------
# Validate area values before doing anything else
# ---------------------------------------------------------------------------
area = config.get("area", {})
if any(area.get(k) is None for k in ("west", "east", "south", "north")):
    print(
        "Error: area values in config.json are null. "
        "Run inspect_dtm.py first, then set the correct projected coordinates."
    )
    sys.exit(1)

west = float(area["west"])
east = float(area["east"])
south = float(area["south"])
north = float(area["north"])

source_path = REPO_ROOT / config["source_dtm"]
output_path = REPO_ROOT / config["cropped_dtm"]

# ---------------------------------------------------------------------------
# Check source file existence before importing rasterio
# ---------------------------------------------------------------------------
if not source_path.exists():
    print(f"Error: source DTM not found at:\n  {source_path}")
    print()
    print("Steps to fix:")
    print("  1. Place the file at that location, or")
    print('  2. Update "source_dtm" in pipeline/config.json to the correct path.')
    sys.exit(1)

# ---------------------------------------------------------------------------
# Crop
# ---------------------------------------------------------------------------
import rasterio  # noqa: E402
import rasterio.windows  # noqa: E402

with rasterio.open(source_path) as ds:
    # Compute window from projected bounding box
    window = rasterio.windows.from_bounds(
        west, south, east, north, transform=ds.transform
    )

    # Clamp to the actual raster extent
    raster_window = rasterio.windows.Window(0, 0, ds.width, ds.height)
    window = window.intersection(raster_window)

    # If intersection is empty the area is entirely outside the raster
    if window.width <= 0 or window.height <= 0:
        print(
            "Error: the area defined in config.json falls entirely outside "
            "the source raster bounds. Check the west/east/south/north values."
        )
        sys.exit(1)

    # Read only the pixels inside the window (REQ-08: no full-file load)
    data = ds.read(1, window=window)

    # Build the corrected transform for the sub-window origin
    new_transform = rasterio.windows.transform(window, ds.transform)

    # Carry forward source metadata
    src_crs = ds.crs
    src_nodata = ds.nodata
    src_dtype = ds.dtypes[0]

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
# Create data/raw/ if it does not exist (REQ-09)
output_path.parent.mkdir(parents=True, exist_ok=True)

with rasterio.open(
    output_path,
    "w",
    driver="GTiff",
    height=data.shape[0],
    width=data.shape[1],
    count=1,
    dtype=src_dtype,
    crs=src_crs,
    transform=new_transform,
    nodata=src_nodata,
    compress="lzw",
) as dst:
    dst.write(data, 1)

size_bytes = output_path.stat().st_size
print(f"{output_path}  {size_bytes}")
