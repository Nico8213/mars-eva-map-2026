# File formats
| File | Written by | Read by | Content |
|---|---|---|---|
| data/processed/grid.json | A | B, C | Source product name and version, pixel size (m), width, height, top-left coordinate, coordinate notes |
| data/processed/slope.npy | A | B | 2D array, degrees, same size as grid.json |
| data/processed/layers/*.png and layers.json | A | C | One semi-transparent PNG per layer; layers.json lists name, file, extent and data card id |
| data/processed/poi.geojson | A | B, C | Points of interest: id, name, type, position, source |
| data/processed/data_cards.json | A | C | One data card per layer: source, version, date, resolution, license, known issues |
| routing/out/route_<name>.geojson | B | C | Route; properties: length, max slope, data used |
| validation/out/report.json | B | C, D | Validation metrics (computed by code), parameters, comparison segments |

Source: PRD v0.3 (`internal/PRD_v0.3.html`), §8.1 (pipeline flow), §8.2 (coordinates), §7.6 (version rule), and §12.6 (open coordinate questions). Items marked TBD are not decided in the PRD. Example values are illustrative unless a PRD section gives the value.

## Common conventions

- All files are UTF-8. JSON files use 2-space indentation.
- Units: lengths in metres, angles in degrees, time in ISO 8601 (UTC).
- Coordinates are projected easting/northing in metres. The CRS name is TBD (PRD §12.6). Do not mix the HiRISE DTM projection with the traverse projection until PRD §8.2 is resolved.
- Every number carries a source and version tag (PRD §7.6). Validation uses only the 2026-10-11 snapshot (sol 1980). New downloads are stored separately.
- Pipeline order (PRD §8.1): freeze snapshot → unify coordinates → slope raster → extract POI → least-cost path on grid → export GeoJSON → cockpit display. Each file below is produced at one of these steps.
- The top-left corner of pixel (row, col) is at easting = top_left.easting_m + col * pixel_size_m and northing = top_left.northing_m - row * pixel_size_m. Northing increases upward; image rows increase downward.

## data/processed/grid.json

Written by A, read by B and C.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `source_product` | string | yes | Name of the source product | `"HiRISE DTM (Jezero crop)"` |
| `source_version` | string | yes | Product version | `"v003"` |
| `source_url` | string | yes | Download or landing page for the source | TBD |
| `pixel_size_m` | number | yes | Pixel size in metres | `1.0` |
| `width` | integer | yes | Number of columns; set after the crop area is fixed | TBD |
| `height` | integer | yes | Number of rows; set after the crop area is fixed | TBD |
| `top_left` | object `{easting_m: number, northing_m: number}` | yes | Coordinates of the top-left pixel corner | TBD |
| `crs` | string | yes | Coordinate reference system name | TBD (PRD §12.6) |
| `coordinate_notes` | string | yes | Projection notes, including the 18.4663° standard parallel question | `"DTM label: equirectangular. Standard parallel 18.4663° meaning TBD (PRD §8.2)."` |
| `elevation_reference` | string | yes | Vertical datum, for example the geoid reference | TBD (PRD §12.6) |
| `nodata_value` | number | yes | Value used for missing pixels | TBD |

Example:

```json
{
  "source_product": "HiRISE DTM (Jezero crop)",
  "source_version": "v003",
  "source_url": "TBD",
  "pixel_size_m": 1.0,
  "width": "TBD",
  "height": "TBD",
  "top_left": { "easting_m": "TBD", "northing_m": "TBD" },
  "crs": "TBD",
  "coordinate_notes": "DTM label: equirectangular. Standard parallel 18.4663° meaning TBD (PRD §8.2).",
  "elevation_reference": "TBD",
  "nodata_value": "TBD"
}
```

Note: `width`, `height`, and the coordinates are shown as strings only because they are not yet known. The real file must hold numbers.

## data/processed/slope.npy

Written by A, read by B. A NumPy array saved with `numpy.save`.

| Property | Value |
|---|---|
| Shape | `(height, width)`, same as `grid.json` |
| Data type | float32 (proposed) |
| Unit | degrees |
| Missing values | NaN (proposed; confirm against `nodata_value`) |
| Derived from | The DTM elevation grid in `grid.json` |

Example load:

```python
import numpy as np
slope = np.load("data/processed/slope.npy")  # shape (height, width), degrees
```

## data/processed/layers/*.png and layers.json

Written by A, read by C.

Each PNG is one semi-transparent RGBA image for one layer. The PRD requires at least three layers: terrain, optical, and spectral (F1). Obstacle (F5) and environment (F9) layers are TBD.

`layers.json` is an array with one object per PNG:

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `name` | string | yes | Layer name shown in the UI | `"Terrain (HiRISE DTM)"` |
| `file` | string | yes | PNG path relative to `data/processed/layers/` | `"terrain.png"` |
| `extent` | object `{min_easting_m, min_northing_m, max_easting_m, max_northing_m}` | yes | Bounding box in the `grid.json` CRS | TBD |
| `data_card_id` | string | yes | Matches an `id` in `data_cards.json` | `"card-terrain-hirise"` |

Example:

```json
[
  {
    "name": "Terrain (HiRISE DTM)",
    "file": "terrain.png",
    "extent": { "min_easting_m": "TBD", "min_northing_m": "TBD", "max_easting_m": "TBD", "max_northing_m": "TBD" },
    "data_card_id": "card-terrain-hirise"
  }
]
```

## data/processed/poi.geojson

Written by A, read by B and C. A GeoJSON `FeatureCollection` of science points of interest (POI). Sources are CRISM and optical imagery (F2, PRD §3.2).

Each feature:

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `geometry.type` | string | yes | `"Point"` | `"Point"` |
| `geometry.coordinates` | [number, number] | yes | `[easting_m, northing_m]` (see note) | TBD |
| `id` | string | yes | Unique POI id | `"poi-001"` |
| `name` | string | yes | Display name | TBD |
| `type` | string | yes | POI category | `"hydrous mineral detection"` |
| `source` | string | yes | `"CRISM"` or `"optical"` | `"CRISM"` |
| `evidence` | string | yes | Basis shown when the user clicks the point (F2) | TBD |
| `selection_rule` | string | no | Rule that selected this POI; the rule is not yet defined (PRD §3.2, §12.5) | TBD |

Example:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": ["TBD", "TBD"] },
      "properties": {
        "id": "poi-001",
        "name": "TBD",
        "type": "hydrous mineral detection",
        "source": "CRISM",
        "evidence": "TBD",
        "selection_rule": "TBD"
      }
    }
  ]
}
```

Note: RFC 7946 assumes longitude/latitude in WGS84. Projected Mars coordinates break that assumption. Decide whether to keep projected coordinates with a `crs` member, or convert (PRD §12.6).

## data/processed/data_cards.json

Written by A, read by C. An array with one data card per layer. Fields follow F8 (data provenance panel) and the 14.3 decision that data cards are P0.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `id` | string | yes | Card id, referenced by `layers.json` | `"card-terrain-hirise"` |
| `layer_name` | string | yes | Layer this card describes | `"Terrain (HiRISE DTM)"` |
| `mission` | string | yes | Source mission | `"MRO"` |
| `instrument` | string | yes | Source instrument | `"HiRISE"` |
| `product` | string | yes | Product name and version | `"DTM v003"` |
| `acquisition_date` | string | yes | Date or range of source data (ISO 8601) | TBD |
| `resolution` | string | yes | Resolution with unit | `"1 m/px"` |
| `license` | string | yes | License or usage terms | TBD (PRD §7.3, §12.7) |
| `known_issues` | array of string | yes | Known artifacts and limits | `["Block offset artifacts", "Seams"]` |
| `confidence_layer` | string or null | yes | Confidence layer file, if any | `"TBD"` |
| `decision_affected` | string | yes | Which route or display decision this layer changes (F10) | TBD |
| `verification_status` | string | yes | One of `decided`, `verified`, `checked`, `candidate`, `proposed`, `TBD` (PRD status legend) | `"candidate"` |
| `source_url` | string | yes | Source page | TBD |

Example:

```json
[
  {
    "id": "card-terrain-hirise",
    "layer_name": "Terrain (HiRISE DTM)",
    "mission": "MRO",
    "instrument": "HiRISE",
    "product": "DTM v003",
    "acquisition_date": "TBD",
    "resolution": "1 m/px",
    "license": "TBD",
    "known_issues": ["Known processing artifacts (PRD §7.1)", "TBD"],
    "confidence_layer": "TBD",
    "decision_affected": "TBD",
    "verification_status": "candidate",
    "source_url": "TBD"
  }
]
```

## routing/out/route_<name>.geojson

Written by B, read by C. One GeoJSON `Feature` per route, with a `LineString` geometry in the same CRS as `grid.json`.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `name` | string | yes | Route name, matches the `<name>` in the file name | `"ea-01"` |
| `start_poi` | string | yes | `id` of the start POI in `poi.geojson` | `"poi-001"` |
| `end_poi` | string | yes | `id` of the end POI | `"poi-002"` |
| `length_m` | number | yes | Route length in metres | TBD |
| `max_slope_deg` | number | yes | Steepest slope along the route, degrees | TBD |
| `slope_threshold_deg` | number | yes | Threshold used to avoid steep ground (F3 requires it to be documented) | TBD |
| `data_used` | array of string | yes | Layer ids that affected the path (F10) | `["terrain", "spectral"]` |
| `cost_function` | string | yes | Cost function description (F3 requires it to be documented) | TBD |
| `generated_from` | string | yes | Commit hash and config used to generate the route | TBD |

Example:

```json
{
  "type": "Feature",
  "geometry": { "type": "LineString", "coordinates": [["TBD", "TBD"], ["TBD", "TBD"]] },
  "properties": {
    "name": "ea-01",
    "start_poi": "poi-001",
    "end_poi": "poi-002",
    "length_m": "TBD",
    "max_slope_deg": "TBD",
    "slope_threshold_deg": "TBD",
    "data_used": ["terrain", "spectral"],
    "cost_function": "TBD",
    "generated_from": "TBD"
  }
}
```

## validation/out/report.json

Written by B, read by C and D. Metrics are computed by code only (PRD §9.4). Parameters are written and locked before the run (PRD §9.2).

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `report_id` | string | yes | Unique run id | `"val-001"` |
| `generated_at` | string | yes | ISO 8601 timestamp (UTC) | TBD |
| `code_commit` | string | yes | Commit hash of the code that produced the run | TBD |
| `snapshot` | object | yes | Traverse snapshot used: `file`, `date`, `sol` | `{"file": "M20_traverse.json", "date": "2026-10-11", "sol": 1980}` |
| `parameters` | object | yes | Locked parameters, including buffer width and slope threshold | TBD |
| `metrics` | object | yes | Computed values. Candidate metrics: `buffer_overlap_ratio`, `dtw_distance`, `mean_segment_deviation_m` (PRD §9.2) | `{"buffer_overlap_ratio": null}` (values filled by code) |
| `comparison_segments` | array of object | yes | Segments compared, each with `segment_id`, `sol_range`, `length_m`, and `selection_reason` (PRD §9.3) | TBD |
| `notes` | string | yes | Honest summary, including any gap and its cause (PRD §9.4) | TBD |

Example (metric values stay `null` until the code computes them):

```json
{
  "report_id": "val-001",
  "generated_at": "TBD",
  "code_commit": "TBD",
  "snapshot": { "file": "M20_traverse.json", "date": "2026-10-11", "sol": 1980 },
  "parameters": { "buffer_width_m": "TBD", "slope_threshold_deg": "TBD" },
  "metrics": {
    "buffer_overlap_ratio": null,
    "dtw_distance": null,
    "mean_segment_deviation_m": null
  },
  "comparison_segments": [
    { "segment_id": "TBD", "sol_range": "TBD", "length_m": "TBD", "selection_reason": "TBD" }
  ],
  "notes": "TBD"
}
```

## Open items that block these files

- CRS name, the meaning of 18.4663°, and the unification of HiRISE and traverse projections (PRD §8.2, §12.6).
- Elevation reference (`elev_geoid`) and SCLK conversion (PRD §12.6).
- POI selection rule (PRD §3.2, §12.5).
- CRISM product page, version, resolution, and license (PRD §7.3, §12.7).
- Obstacle layer source (F5) and environment layer source (F9, §7.7).
