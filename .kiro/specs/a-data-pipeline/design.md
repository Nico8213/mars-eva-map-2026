# Design: a-data-pipeline

## Architecture overview

```
../local_only/hirise_raw/
  JEZ_hirise_soc_006_DTM_1m.tif   (source, outside repo, never committed)
           │
           ▼  pipeline/step1_crop_dtm.py
           │   rasterio windowed read bounded by config.json "area"
           │
  data/raw/cropped_dtm.tif          (intermediate, not committed)
           │
     ┌─────┴─────────────────┐
     ▼                       ▼
pipeline/step2_slope.py    pipeline/step3_layers.py
   slope array (scipy)         PNG rendering (scikit-image / pillow)
   grid metadata                hillshade (numpy)
     │                              │
     ▼                              ▼
data/processed/slope.npy      data/processed/layers/slope.png
data/processed/grid.json      data/processed/layers/hillshade.png
                               data/processed/layers/layers.json
```

Each step is independent on disk: step2 and step3 both read `data/raw/cropped_dtm.tif`
so they can be re-run without repeating step1.

---

## Step 1 — Crop DTM (`pipeline/step1_crop_dtm.py`)

**Goal:** extract the region of interest from the large source GeoTIFF using rasterio
windowed reads and write a smaller intermediate GeoTIFF.

**Algorithm:**
1. Read `config.json` to get `source_dtm`, `area` bounds, and `cropped_dtm` output path.
2. Open the source file with `rasterio.open()` (no data loaded yet).
3. Convert the `area` bounding box (projected coordinates) to a rasterio `Window`
   using `rasterio.windows.from_bounds()` and `ds.transform`.
4. Read band 1 through that window only: `ds.read(1, window=window)`.
5. Build a new transform with `rasterio.windows.transform(window, ds.transform)`.
6. Write the cropped array to `data/raw/cropped_dtm.tif` using the same CRS, dtype,
   nodata value, and compression as the source.
7. Print: path and byte size of `cropped_dtm.tif`.

**Key rasterio calls:**
```python
window = rasterio.windows.from_bounds(west, south, east, north, transform=ds.transform)
window = window.intersection(rasterio.windows.Window(0, 0, ds.width, ds.height))
data = ds.read(1, window=window)
new_transform = rasterio.windows.transform(window, ds.transform)
```

---

## Step 2 — Slope and grid metadata (`pipeline/step2_slope.py`)

**Goal:** compute per-pixel slope in degrees from the cropped DTM and write `slope.npy`
and `grid.json`.

**Algorithm:**
1. Read `config.json`.
2. Open `data/raw/cropped_dtm.tif` with rasterio.
3. Read band 1 as float32.  Replace nodata values with `np.nan`.
4. Compute slope:
   - Retrieve pixel size `dx` from the transform (in metres).
   - Use `np.gradient(elevation, dx, axis=0)` and `np.gradient(elevation, dx, axis=1)`
     to get rise/run in both directions (dz/dy, dz/dx).
   - `slope_rad = np.arctan(np.sqrt((dz_dx)**2 + (dz_dy)**2))`
   - `slope_deg = np.degrees(slope_rad).astype(np.float32)`
   - Pixels where elevation is nodata remain `np.nan`.
5. Save `slope_deg` to `data/processed/slope.npy` with `np.save()`.
6. Build `grid.json`:
   - `source_product`, `version`, `doi` from constants (REQ-04).
   - `crs_wkt` from `ds.crs.wkt`.
   - `pixel_size_m` from `abs(ds.transform.a)`.
   - `width`, `height` from `ds.width`, `ds.height`.
   - `top_left_coordinate`: reproject the top-left corner of the cropped window from
     the native projected CRS to geographic using `rasterio.warp.transform()` with
     `dst_crs="EPSG:49900"` (IAU Mars 2000 geographic, closest available; fall back to
     `"+proj=longlat +a=3396190 +b=3376200 +no_defs"` if unavailable).
   - `coordinate_notes` describing the reprojection.
7. Write `grid.json` with `json.dump(..., indent=2)`.
8. Print path and size of each output file.

**CRS note:** EPSG:49900 may not be in all rasterio/PROJ installs.  The fallback
Proj4 string `"+proj=longlat +a=3396190 +b=3376200 +no_defs"` uses the IAU Mars
tri-axial ellipsoid semi-major/semi-minor axes and is equivalent for this purpose.

---

## Step 3 — Layer PNGs (`pipeline/step3_layers.py`)

**Goal:** produce 8-bit single-channel PNGs suitable for `L.imageOverlay` in Leaflet.

**Algorithm:**

### 3a — Slope PNG
1. Load `slope.npy`.
2. Load `grid.json` to get `slope_colormap_max_deg` from `config.json` (default 45).
3. Normalise: `img = np.clip(slope / max_deg, 0, 1)` → scale to `[0, 255]` uint8.
4. Write `data/processed/layers/slope.png` with `PIL.Image`.

### 3b — Hillshade PNG
1. Open `data/raw/cropped_dtm.tif`, read as float32.
2. Compute hillshade with standard azimuth 315° and altitude 45°:
   ```
   dx = pixel_size_m
   dz_dx, dz_dy = np.gradient(elev, dx)
   # surface normal
   zenith_rad = np.radians(90 - altitude)
   azimuth_rad = np.radians(360 - azimuth + 90)
   hillshade = (cos(zenith) * cos(arctan(sqrt(dz_dx**2+dz_dy**2))) +
                sin(zenith) * sin(arctan(...)) * cos(azimuth - arctan2(dz_dy, dz_dx)))
   ```
3. Clip to [0, 1], scale to [0, 255] uint8.
4. Write `data/processed/layers/hillshade.png`.

### 3c — layers.json
1. Reproject the four corners of the cropped window from native CRS to geographic
   (same method as step 2) to build the `extent` object.
2. Write `layers.json` as a JSON array with two entries (slope, hillshade), matching
   the schema in REQ-06.
3. Print path and size for each file written.

---

## config.json design

```json
{
  "source_dtm": "../local_only/hirise_raw/JEZ_hirise_soc_006_DTM_1m.tif",
  "area": {
    "west":  null,
    "east":  null,
    "south": null,
    "north": null
  },
  "cropped_dtm": "data/raw/cropped_dtm.tif",
  "slope_colormap_max_deg": 45
}
```

The `source_dtm` path uses `..` to point one level above the repository root, keeping
the raw file outside the repository entirely.  Scripts must resolve all paths relative
to the repository root using `pathlib.Path(__file__).parent.parent` as the base,
so they work regardless of the working directory from which they are invoked.

The `area` values are `null` until the user runs `inspect_dtm.py`, reads the real
raster bounds and CRS, and fills in the correct projected coordinates.  No coordinate
numbers may be written into `config.json` before that inspection.

---

## Error handling policy
- If the source GeoTIFF is missing, the scripts must exit with a clear message and
  `sys.exit(1)` rather than a traceback.
- If the `area` window falls entirely outside the raster extent, exit with an error.
- If `data/raw/` does not exist, create it before writing.

---

## Dependencies (already in pipeline/requirements.txt)
- rasterio 1.5.x — raster I/O and windowed reads
- numpy 2.x — array maths
- scipy 1.x — available but not needed for slope (numpy gradient is sufficient)
- Pillow 13.x — PNG writing
- scikit-image 0.27.x — available if needed for future colour mapping

No new packages are required.
