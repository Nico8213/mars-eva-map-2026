"""
step6_ctx.py — Crop the CTX orthomosaic to the DTM area and render ctx.png.

Reads (config from pipeline/config.json only):
  source_ctx, area (west/east/south/north), cropped_dtm
  data/raw/cropped_dtm.tif              — only for the CRS comparison
  data/processed/layers/hillshade.png   — only for the visual check image

Writes:
  data/processed/layers/ctx.png                 — 8-bit grayscale, 2-98 percentile stretch
  data/processed/layers/layers.json             — "CTX" entry added/replaced
  data/raw/ctx_vs_hillshade_check.png           — side-by-side check (not committed)

The CTX is read with a windowed read at its native pixel size (no resampling).
The window is snapped outward to whole CTX pixels, so the written extent is
computed from the window actually read, not from the requested area.

Usage:
    .venv/Scripts/python.exe pipeline/step6_ctx.py
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

area = config.get("area", {})
if any(area.get(k) is None for k in ("west", "east", "south", "north")):
    print("Error: area values in config.json are missing or null.")
    sys.exit(1)
west, east = float(area["west"]), float(area["east"])
south, north = float(area["south"]), float(area["north"])

if not config.get("source_ctx"):
    print('Error: "source_ctx" is missing from pipeline/config.json.')
    sys.exit(1)

# Resolved against the repo root, like the other pipeline steps.
source_ctx_path = (REPO_ROOT / config["source_ctx"]).resolve()
cropped_dtm_path = REPO_ROOT / config["cropped_dtm"]

layers_dir = REPO_ROOT / "data" / "processed" / "layers"
ctx_png_path = layers_dir / "ctx.png"
hillshade_png_path = layers_dir / "hillshade.png"
layers_json_path = layers_dir / "layers.json"
check_png_path = REPO_ROOT / "data" / "raw" / "ctx_vs_hillshade_check.png"

for label, p, hint in (
    ("CTX source", source_ctx_path, 'Check "source_ctx" in pipeline/config.json.'),
    ("cropped DTM", cropped_dtm_path, "Run step1_crop_dtm.py first."),
    ("hillshade.png", hillshade_png_path, "Run step3_layers.py first."),
    ("layers.json", layers_json_path, "Run step3_layers.py first."),
):
    if not p.exists():
        print(f"Error: {label} not found at:\n  {p}\n{hint}")
        sys.exit(1)

import rasterio  # noqa: E402
import rasterio.warp  # noqa: E402
import rasterio.windows  # noqa: E402
from rasterio.windows import Window  # noqa: E402
from PIL import Image  # noqa: E402

# ---------------------------------------------------------------------------
# CRS check, then windowed read at native resolution
# ---------------------------------------------------------------------------
with rasterio.open(cropped_dtm_path) as dtm:
    dtm_crs = dtm.crs

with rasterio.open(source_ctx_path) as ds:
    if ds.crs != dtm_crs:
        print(
            "Error: CTX CRS does not match the DTM CRS. Nothing was written.\n"
            f"  CTX: {ds.crs}\n"
            f"  DTM: {dtm_crs}\n"
            "Reproject the CTX to the DTM CRS first (outside this script)."
        )
        sys.exit(1)

    win = rasterio.windows.from_bounds(west, south, east, north, transform=ds.transform)
    # Snap outward to whole pixels so no resampling is needed.
    col_off = math.floor(win.col_off)
    row_off = math.floor(win.row_off)
    col_end = math.ceil(win.col_off + win.width)
    row_end = math.ceil(win.row_off + win.height)
    win = Window(col_off, row_off, col_end - col_off, row_end - row_off)
    win = win.intersection(Window(0, 0, ds.width, ds.height))
    if win.width <= 0 or win.height <= 0:
        print("Error: the area in config.json lies outside the CTX raster bounds.")
        sys.exit(1)

    band = ds.read(1, window=win, masked=True)
    win_transform = rasterio.windows.transform(win, ds.transform)
    ctx_crs = ds.crs
    px_x, px_y = abs(ds.transform.a), abs(ds.transform.e)

height, width = band.shape
data = band.astype(np.float64).filled(np.nan)
valid = ~np.ma.getmaskarray(band) & np.isfinite(data)
if not valid.any():
    print("Error: the CTX crop contains no valid pixels.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2nd-98th percentile stretch -> 8-bit; nodata becomes transparent
# ---------------------------------------------------------------------------
lo, hi = np.percentile(data[valid], [2, 98])
if hi <= lo:
    print(f"Error: degenerate percentile range (p2={lo}, p98={hi}).")
    sys.exit(1)
gray = np.zeros(data.shape, dtype=np.uint8)
gray[valid] = (np.clip((data[valid] - lo) / (hi - lo), 0.0, 1.0) * 255).round().astype(np.uint8)

layers_dir.mkdir(parents=True, exist_ok=True)
if valid.all():
    Image.fromarray(gray, mode="L").save(ctx_png_path)
else:
    alpha = np.where(valid, 255, 0).astype(np.uint8)
    Image.fromarray(np.dstack([gray, alpha]), mode="LA").save(ctx_png_path)

# ---------------------------------------------------------------------------
# Extent in degrees (same method as step3), from the window actually read
# ---------------------------------------------------------------------------
GEO_CRS_PRIMARY = "EPSG:49900"
GEO_CRS_FALLBACK = "+proj=longlat +a=3396190 +b=3376200 +no_defs"

w_edge = win_transform.c
n_edge = win_transform.f
e_edge = w_edge + width * win_transform.a
s_edge = n_edge + height * win_transform.e  # e is negative
xs = [w_edge, e_edge, w_edge, e_edge]
ys = [n_edge, n_edge, s_edge, s_edge]
try:
    lons, lats = rasterio.warp.transform(ctx_crs, GEO_CRS_PRIMARY, xs, ys)
except Exception:
    lons, lats = rasterio.warp.transform(ctx_crs, GEO_CRS_FALLBACK, xs, ys)
extent = {
    "west": float(min(lons)),
    "east": float(max(lons)),
    "south": float(min(lats)),
    "north": float(max(lats)),
}

with open(layers_json_path) as f:
    layers = json.load(f)
layers = [l for l in layers if l.get("data_card_id") != "ctx_orthomosaic_008"]
layers.append(
    {
        "name": "CTX",
        "file": "layers/ctx.png",
        "extent": extent,
        "data_card_id": "ctx_orthomosaic_008",
    }
)
with open(layers_json_path, "w") as f:
    json.dump(layers, f, indent=2)

# ---------------------------------------------------------------------------
# Visual check: ctx.png | hillshade.png, same size (check image only;
# ctx.png itself stays at native resolution)
# ---------------------------------------------------------------------------
hs = Image.open(hillshade_png_path).convert("L")
ctx_img = Image.open(ctx_png_path)
if ctx_img.mode == "LA":
    bg = Image.new("L", ctx_img.size, 0)
    bg.paste(ctx_img.getchannel(0), mask=ctx_img.getchannel(1))
    ctx_img = bg
ctx_img = ctx_img.convert("L").resize(hs.size, Image.BILINEAR)
check = Image.new("L", (hs.width * 2, hs.height))
check.paste(ctx_img, (0, 0))
check.paste(hs, (hs.width, 0))
check_png_path.parent.mkdir(parents=True, exist_ok=True)
check.save(check_png_path)

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
print(f"CTX pixel size: {px_x} x {px_y} (CRS units)")
print(f"CTX crop shape (rows, cols): {band.shape}")
print(f"Stretch: p2={lo}, p98={hi}")
for path in (ctx_png_path, layers_json_path, check_png_path):
    print(f"{path}  {path.stat().st_size}")
