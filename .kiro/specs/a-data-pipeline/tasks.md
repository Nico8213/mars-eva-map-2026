# Tasks: a-data-pipeline

## Task list

- [x] 1. Create pipeline/config.json
- [x] 2. Create pipeline/inspect_dtm.py (helper — not part of the main pipeline)
- [x] 3. Create pipeline/step1_crop_dtm.py
- [x] 4. Create pipeline/step2_slope.py
- [ ] 5. Create pipeline/step3_layers.py
- [x] 6. Add data/raw/ to .gitignore

---

## Task 1 — Create `pipeline/config.json`

Create `pipeline/config.json` with the following content.  The `area` values are
placeholder estimates; the user must update them after running `inspect_dtm.py`.

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

Acceptance:
- File exists at `pipeline/config.json`.
- File is valid JSON with keys: `source_dtm`, `area` (with sub-keys west/east/south/north),
  `cropped_dtm`, `slope_colormap_max_deg`.

---

## Task 2 — Create `pipeline/inspect_dtm.py`

A short utility that opens the source GeoTIFF (without reading pixel data) and prints:
- File path and size in bytes
- Raster width × height
- CRS (PROJ4 and WKT)
- Transform (affine coefficients)
- Bounding box in native projected coordinates
- Nodata value
- Dtype of band 1

This script is used to verify that the `area` values in `config.json` fall inside the
raster extent before committing to a full run.

The script reads `source_dtm` from `pipeline/config.json` and resolves the path
relative to the repository root (i.e. `pathlib.Path(__file__).parent.parent / source_dtm`).

Acceptance:
- Script runs with `.venv\Scripts\python.exe pipeline/inspect_dtm.py` from repo root.
- Prints all fields listed above.
- Exits cleanly if the file is missing with a helpful message.

---

## Task 3 — Create `pipeline/step1_crop_dtm.py`

Implement the windowed-read crop described in design.md § Step 1.

Acceptance:
- Script runs from the command line with no arguments.
- Uses `rasterio.windows.from_bounds()` to compute the window; never calls `ds.read()`
  without a `window=` argument.
- Creates `data/raw/` if it does not exist.
- Writes `data/raw/cropped_dtm.tif` with:
  - Same CRS as the source
  - Correct new transform reflecting the sub-window origin
  - Same nodata value as the source
  - LZW compression
- Prints exactly: `path  size_bytes` for the output file.
- If any of `area.west`, `area.east`, `area.south`, `area.north` is `null`, print
  `"Error: area values in config.json are null. Run inspect_dtm.py first, then set
  the correct projected coordinates."` and exit with code 1.  Do not proceed.
- If the source file is missing, print an error and exit with code 1.
- If the `area` window is entirely outside the raster bounds, print an error and exit with code 1.

---

## Task 4 — Create `pipeline/step2_slope.py`

Implement slope calculation and grid.json writing described in design.md § Step 2.

Acceptance:
- Reads `data/raw/cropped_dtm.tif` (must already exist).
- Computes slope using `np.gradient` with the correct pixel size in metres.
- Writes `data/processed/slope.npy` as float32.
- Writes `data/processed/grid.json` with all nine keys from REQ-05:
  `source_product`, `version`, `doi`, `crs_wkt`, `pixel_size_m`, `width`, `height`,
  `top_left_coordinate`, `coordinate_notes`.
- `source_product` is `"JEZ_hirise_soc_006_DTM_1m"`, `version` is `"006"`,
  `doi` is `"10.5066/P9REJ9JN"` — these are constants in the script, not read from
  the GeoTIFF (they cannot be changed by the user; they describe a known data product).
- `top_left_coordinate` is computed by reprojecting, not invented.
- Prints `path  size_bytes` for `slope.npy` and `grid.json`.

---

## Task 5 — Create `pipeline/step3_layers.py`

Implement layer PNG and layers.json writing described in design.md § Step 3.

Acceptance:
- Reads `data/processed/slope.npy` and `data/raw/cropped_dtm.tif`.
- Writes `data/processed/layers/slope.png` — 8-bit grayscale, 0 = 0°, 255 = max_deg
  from config.
- Writes `data/processed/layers/hillshade.png` — 8-bit grayscale hillshade.
- Writes `data/processed/layers/layers.json` as a JSON array with two objects
  (slope first, hillshade second), each with keys `name`, `file`, `extent`,
  `data_card_id`.
- `extent` values are geographic degrees derived by reprojection, not invented.
- `data_card_id` for the slope layer is `"hirise_dtm_006"`;
  for hillshade it is `"hirise_dtm_006"` (same source).
- Prints `path  size_bytes` for each of the three files written.

---

## Task 6 — Update `.gitignore`

Ensure the following lines are present in `.gitignore` (add if missing, do not
duplicate if already present):

```
data/raw/
```

Note: `../local_only/` is outside the repository entirely and requires no `.gitignore`
entry.  `data/raw/` holds intermediate rasters inside the repo that must not be
committed.

Acceptance:
- `.gitignore` contains `data/raw/`.
- `data/processed/` is NOT ignored (processed outputs are committed).
- There is no entry for `local_only/` (that directory no longer exists inside the repo).
