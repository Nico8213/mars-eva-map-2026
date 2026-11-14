# Requirements: a-data-pipeline

## Overview
Process the HiRISE-derived 1 m/px Digital Terrain Model (DTM) of Jezero Crater into
slope, hillshade, and grid metadata files consumed by the routing engine (B) and the
web map (C).  Every number must come from the source data; nothing is invented.

## Requirements

### REQ-01 Input and area
- The source elevation raster is at `../local_only/hirise_raw/JEZ_hirise_soc_006_DTM_1m.tif`
  (one level above the repository root, outside the repository).
- All scripts must read this path from `pipeline/config.json` only.  No script may
  hard-code any path to the source file.
- The area to process is defined by the `"area"` object in `pipeline/config.json`.
  The area object contains `west`, `east`, `south`, `north` in the native projected
  coordinate reference system (CRS) of the GeoTIFF.
- The pipeline must use rasterio windowed reads to load only the pixels that fall
  inside the area rectangle.  The full file must never be loaded into memory.

### REQ-02 Outputs
| File | Content |
|---|---|
| `data/processed/slope.npy` | 2-D float32 array, slope in degrees, row-major, same CRS/extent as the cropped window |
| `data/processed/grid.json` | Metadata described in REQ-05 |
| `data/processed/layers/slope.png` | 8-bit single-channel PNG, slope colourised (0–45 °) |
| `data/processed/layers/hillshade.png` | 8-bit single-channel PNG, hillshade derived from the DTM |
| `data/processed/layers/layers.json` | Layer manifest described in REQ-06 |

### REQ-03 Coordinate convention
- `grid.json` stores geographic (lat/lon) coordinates for `top_left_coordinate` so
  that the web map (C) can position overlays without needing the projected CRS.
- The CRS must be re-projected from the source projection to geographic
  (IAU 2015 Mars Geographic, EPSG:49900 or equivalent) for that field only.
  All array dimensions, pixel sizes, and extents stored elsewhere in `grid.json`
  remain in the native projected CRS of the source file.

### REQ-04 Source attribution
- Do not invent any metadata.  The source product name, version, and DOI must be
  recorded exactly as known from the USGS data release:
  - `source_product`: `"JEZ_hirise_soc_006_DTM_1m"`
  - `version`: `"006"`
  - `doi`: `"10.5066/P9REJ9JN"`

### REQ-05 grid.json fields
The file must contain exactly these top-level keys:

| Key | Type | Description |
|---|---|---|
| `source_product` | string | Product name (see REQ-04) |
| `version` | string | Product version (see REQ-04) |
| `doi` | string | USGS DOI (see REQ-04) |
| `crs_wkt` | string | WKT string of the native projected CRS read from the GeoTIFF |
| `pixel_size_m` | number | Pixel size in metres (from GeoTIFF transform; must equal 1.0 for this product) |
| `width` | integer | Pixel width of the cropped window |
| `height` | integer | Pixel height of the cropped window |
| `top_left_coordinate` | object | `{"latitude": <float>, "longitude": <float>}` in geographic degrees |
| `coordinate_notes` | string | Human-readable note about the CRS and re-projection |

### REQ-06 layers.json fields
Array of layer objects.  Each object contains:

| Key | Type | Description |
|---|---|---|
| `name` | string | Human-readable layer name |
| `file` | string | Path relative to `data/processed/` |
| `extent` | object | `{"west": <float>, "south": <float>, "east": <float>, "north": <float>}` in geographic degrees |
| `data_card_id` | string | Identifier matching a future entry in `data_cards.json` |

### REQ-07 Script organisation
- Each logical step is a separate script in `pipeline/`:
  - `pipeline/step1_crop_dtm.py` — windowed read, writes a cropped intermediate GeoTIFF to `data/raw/`
  - `pipeline/step2_slope.py` — computes slope from the cropped GeoTIFF, writes `slope.npy` and `grid.json`
  - `pipeline/step3_layers.py` — renders slope PNG and hillshade PNG, writes `layers.json`
- Each script must be runnable from the command line with no arguments (all parameters
  come from `pipeline/config.json`).
- At the end of execution each script prints one line per output file: path and size in bytes.

### REQ-08 Memory constraint
- The pipeline must never load the full source GeoTIFF into memory.  rasterio
  windowed reads must be used in `step1_crop_dtm.py`.  Window is computed from
  the `area` bounds in `config.json`.

### REQ-09 Repository hygiene
- Raw rasters live in `../local_only/` (one level above the repo root, never inside it)
  or in `data/raw/` (inside the repo but excluded by `.gitignore`).  Neither location
  is committed to the repository.
- `data/processed/` files (`.npy`, `.json`, `.png`) are committed.
- No hard-coded absolute paths.  All paths in scripts are relative to the repository
  root and are read from `pipeline/config.json`.

### REQ-10 config.json
`pipeline/config.json` must exist and contain at minimum:

```json
{
  "source_dtm": "../local_only/hirise_raw/JEZ_hirise_soc_006_DTM_1m.tif",
  "area": {
    "west":  <projected X, metres>,
    "east":  <projected X, metres>,
    "south": <projected Y, metres>,
    "north": <projected Y, metres>
  },
  "cropped_dtm": "data/raw/cropped_dtm.tif",
  "slope_colormap_max_deg": 45
}
```
The `source_dtm` path is relative to the repository root (`..` resolves to
`C:\SpaceApps2026` on the current machine).  Scripts must resolve it with
`pathlib.Path(__file__).parent.parent / config["source_dtm"]` or equivalent so
the path works regardless of the working directory from which a script is invoked.
The `area` values are set to `null` until the user runs `inspect_dtm.py`, reads the
real raster bounds and CRS, and fills in the correct projected coordinates.
No coordinate numbers may be written into `config.json` before that inspection.
