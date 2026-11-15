# Interface specification: file formats

This document describes the files that the data pipeline, the routing code, the validation code and the web page exchange. Each file has one writer and one or more readers.

Values written in angle brackets, such as `<integer>`, are placeholders that show the type. They are not real data. The real values are in the files themselves.

| File | Written by | Read by | Content |
| --- | --- | --- | --- |
| `data/processed/grid.json` | Pipeline | Routing, Web | Source product name and version, pixel size (m), width, height, top-left coordinate, coordinate system, known issues |
| `data/processed/slope.npy` | Pipeline | Routing | 2D array of slope in degrees, same size as the grid |
| `data/processed/layers/*.png` and `layers.json` | Pipeline | Web | One semi-transparent PNG per layer; `layers.json` lists name, file, extent and data card id |
| `data/processed/poi.geojson` | Pipeline | Routing, Web | Points of interest: id, name, type, position, source, evidence |
| `data/processed/data_cards.json` | Pipeline | Web | One data card per layer: source, version, date, resolution, license, known issues |
| `routing/out/route_<name>.geojson` | Routing | Web | Route; properties include length, maximum slope and data used |
| `validation/out/report.json` | Validation | Web | Validation metrics (computed by code), locked parameters, compared segments |

## Common conventions

- All files are UTF-8. JSON files use 2-space indentation.
- Units: lengths in metres, angles in degrees, time in ISO 8601 (UTC).
- Grid coordinates are projected easting/northing in metres. The grid coordinate system is the one of the HiRISE DTM: equirectangular, true-scale latitude 0, central meridian 0, Mars sphere with radius R = 3396190 m. The 18.4663° standard parallel used by the PLACES map convention is not used.
- Every number carries a source and a version. All sources are listed in `docs/CITATIONS.md`.
- The top-left corner of pixel (row, col) is at easting = top-left easting + col × pixel size and northing = top-left northing − row × pixel size. Northing increases upward; image rows increase downward. The pixel centre is at the corner position plus half a pixel.
- Pipeline order: download and crop the DTM → unify coordinates → slope raster → points of interest → least-cost path on the grid → export GeoJSON → web display. Each file below is produced at one of these steps.
- Validation reference: Mars 2020 Rover PLACES `best_interp.csv` (Release 16), frozen as a snapshot before the validation run. The NASA/JPL MMGIS traverse and waypoint files are used only as a cross-check. Both are listed in `docs/CITATIONS.md`.
- Validation distances are computed in a local azimuthal equidistant projection centred on the grid centre (`+proj=aeqd +R=3396190`).
- Latitude type: PLACES latitudes are planetocentric. For the MMGIS files the official documentation does not state the latitude type, and this project does not state one either.

## data/processed/grid.json

Written by the pipeline, read by routing and web.

| Field | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `source_product` | string | yes | Name of the source product | `"Mars 2020 TRN HiRISE DTM mosaic (Jezero crop)"` |
| `source_version` | string | yes | Product version | `"006"` |
| `source_url` | string | yes | DOI or landing page of the source | `"https://doi.org/10.5066/P9REJ9JN"` |
| `pixel_size_m` | number | yes | Pixel size in metres | `1.0` |
| `width` | integer | yes | Number of columns | `<integer>` |
| `height` | integer | yes | Number of rows | `<integer>` |
| `top_left` | object `{easting_m: number, northing_m: number}` | yes | Coordinates of the outer corner of the top-left pixel | `<numbers>` |
| `crs` | string | yes | Coordinate system name | see example below |
| `coordinate_notes` | string | yes | Projection notes | see example below |
| `elevation_reference` | string | yes | Vertical datum as stated by the source product | `<string>` |
| `nodata_value` | number | yes | Value used for missing pixels | `<number>` |

Example (placeholders are strings here only so that the example stays valid JSON; the real file holds numbers):

```json
{
  "source_product": "Mars 2020 TRN HiRISE DTM mosaic (Jezero crop)",
  "source_version": "006",
  "source_url": "https://doi.org/10.5066/P9REJ9JN",
  "pixel_size_m": 1.0,
  "width": "<integer>",
  "height": "<integer>",
  "top_left": { "easting_m": "<number>", "northing_m": "<number>" },
  "crs": "Equirectangular, true-scale latitude 0, central meridian 0, Mars sphere R = 3396190 m",
  "coordinate_notes": "The 18.4663 degree standard parallel of the PLACES map convention is not used.",
  "elevation_reference": "<string>",
  "nodata_value": "<number>"
}
```

## data/processed/slope.npy

Written by the pipeline, read by routing. A NumPy array saved with `numpy.save`.

| Property | Value |
| --- | --- |
| Shape | `(height, width)`, same as `grid.json` |
| Data type | float32 |
| Unit | degrees |
| Missing values | NaN |
| Derived from | The DTM elevation grid described in `grid.json` |

Known issue: the slope script uses 1 m spacing in both the north-south and the east-west direction. The real east-west ground spacing is about 0.95 m, so the east-west part of the slope is understated by about 5%. The raster was not recomputed.

Example load:

```python
import numpy as np
slope = np.load("data/processed/slope.npy")  # shape (height, width), degrees
```

## data/processed/layers/*.png and layers.json

Written by the pipeline, read by web.

Each PNG is one semi-transparent RGBA image for one layer. The Optical layer comes from the CTX mosaic (6 m/px) and is used as visual background only; it does not affect route cost. There is no spectral layer: spectral (CRISM) information is a reference only and is not drawn on the map.

`layers.json` is an array with one object per PNG:

| Field | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `name` | string | yes | Layer name shown on the web page | `"Optical (CTX 6 m)"` |
| `file` | string | yes | PNG path relative to `data/processed/layers/` | `"<file name>.png"` |
| `extent` | object `{min_easting_m, min_northing_m, max_easting_m, max_northing_m}` | yes | Bounding box in the `grid.json` coordinate system | `<numbers>` |
| `data_card_id` | string | yes | Matches an `id` in `data_cards.json` | `"<card id>"` |

Example:

```json
[
  {
    "name": "Optical (CTX 6 m)",
    "file": "<file name>.png",
    "extent": {
      "min_easting_m": "<number>",
      "min_northing_m": "<number>",
      "max_easting_m": "<number>",
      "max_northing_m": "<number>"
    },
    "data_card_id": "<card id>"
  }
]
```

## data/processed/poi.geojson

Written by the pipeline, read by routing and web. A GeoJSON `FeatureCollection` of points of interest (POI). The POIs were selected by eye from `hillshade.png`. They are not CRISM detections.

Each feature:

| Property | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `geometry.type` | string | yes | `"Point"` | `"Point"` |
| `geometry.coordinates` | [number, number] | yes | `[easting_m, northing_m]` in the `grid.json` coordinate system | `<numbers>` |
| `id` | string | yes | Unique POI id | `"<id>"` |
| `name` | string | yes | Display name | `"Cliff A"` |
| `type` | string | yes | POI category | `"<category>"` |
| `source` | string | yes | Image the point was selected from | `"hillshade"` |
| `evidence` | string | yes | Basis shown when the user clicks the point | `"Selected by eye from hillshade.png; not a CRISM detection"` |
| `selection_rule` | string | no | Rule that selected this POI | `"Selected by eye; no automatic rule"` |

Example:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": ["<number>", "<number>"] },
      "properties": {
        "id": "<id>",
        "name": "Cliff A",
        "type": "<category>",
        "source": "hillshade",
        "evidence": "Selected by eye from hillshade.png; not a CRISM detection",
        "selection_rule": "Selected by eye; no automatic rule"
      }
    }
  ]
}
```

Note: the GeoJSON standard (RFC 7946) assumes longitude/latitude on Earth (WGS84). The coordinates in this project are projected Mars metres in the grid coordinate system, so a generic GeoJSON viewer will place the points in the wrong place.

## data/processed/data_cards.json

Written by the pipeline, read by web. An array with one data card per layer.

| Field | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `id` | string | yes | Card id, referenced by `layers.json` | `"<card id>"` |
| `layer_name` | string | yes | Layer this card describes | `"Optical (CTX 6 m)"` |
| `mission` | string | yes | Source mission | `"MRO"` |
| `instrument` | string | yes | Source instrument | `"CTX"` |
| `product` | string | yes | Product name and version | `"CTX orthomosaic 008"` |
| `acquisition_date` | string | yes | Date or range of the source data (ISO 8601) | `"<date or range>"` |
| `resolution` | string | yes | Resolution with unit | `"6 m/px"` |
| `license` | string | yes | License or usage terms | `"CC0 1.0 Universal; please cite Fergason et al., 2020"` |
| `known_issues` | array of string | yes | Known artifacts and limits | `["<issue>"]` |
| `confidence_layer` | string or null | yes | Confidence layer file, if any | `null` |
| `decision_affected` | string | yes | Which route or display decision this layer changes | `"Visual background only; not used in route cost"` |
| `verification_status` | string | yes | Status of the facts on the card | `"<status>"` |
| `source_url` | string | yes | Source page | `"https://doi.org/10.5066/P9GV1ND3"` |

Example:

```json
[
  {
    "id": "<card id>",
    "layer_name": "Optical (CTX 6 m)",
    "mission": "MRO",
    "instrument": "CTX",
    "product": "CTX orthomosaic 008",
    "acquisition_date": "<date or range>",
    "resolution": "6 m/px",
    "license": "CC0 1.0 Universal; please cite Fergason et al., 2020",
    "known_issues": ["<issue>"],
    "confidence_layer": null,
    "decision_affected": "Visual background only; not used in route cost",
    "verification_status": "<status>",
    "source_url": "https://doi.org/10.5066/P9GV1ND3"
  }
]
```

For a card about the terrain slope, `known_issues` must include the east-west slope issue described under `slope.npy`.

## routing/out/route_<name>.geojson

Written by routing, read by web. One GeoJSON `Feature` per route, with a `LineString` geometry in the `grid.json` coordinate system.

| Property | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `name` | string | yes | Route name, matches the `<name>` in the file name | `"<name>"` |
| `start_poi` | string | yes | `id` of the start point in `poi.geojson` | `"<id>"` |
| `end_poi` | string | yes | `id` of the end point in `poi.geojson` | `"<id>"` |
| `length_m` | number | yes | Route length in metres | `<number>` |
| `max_slope_deg` | number | yes | Steepest slope along the route, in degrees | `<number>` |
| `slope_threshold_deg` | number | yes | Slope threshold used to avoid steep ground | `<number>` |
| `data_used` | array of string | yes | Data that affected the path | `["slope"]` |
| `cost_function` | string | yes | Short description of the cost function; full text in `docs/research/nico-routing-spec.md` | `"<description>"` |
| `generated_from` | string | yes | Commit hash and parameter file used to generate the route | `"<commit hash>"` |

Example:

```json
{
  "type": "Feature",
  "geometry": { "type": "LineString", "coordinates": [["<number>", "<number>"], ["<number>", "<number>"]] },
  "properties": {
    "name": "<name>",
    "start_poi": "<id>",
    "end_poi": "<id>",
    "length_m": "<number>",
    "max_slope_deg": "<number>",
    "slope_threshold_deg": "<number>",
    "data_used": ["slope"],
    "cost_function": "<description>",
    "generated_from": "<commit hash>"
  }
}
```

## validation/out/report.json

Written by validation, read by web. All metric values are computed by code. The parameters are written to `validation/params.json` and locked before any validation run.

| Field | Type | Required | Description | Example |
| --- | --- | --- | --- | --- |
| `report_id` | string | yes | Unique run id | `"<id>"` |
| `generated_at` | string | yes | ISO 8601 timestamp (UTC) | `"<timestamp>"` |
| `code_commit` | string | yes | Commit hash of the code that produced the run | `"<commit hash>"` |
| `reference` | object | yes | Reference data used: `file`, `release`, `downloaded`, `sha256`, `sol_range` | see example below |
| `parameters` | object | yes | Locked parameters, copied from `validation/params.json` | `<object>` |
| `metrics` | object | yes | Computed values; names are defined in `docs/research/nico-routing-spec.md` | `{"end_point_error_m": null}` |
| `comparison_segments` | array of object | yes | Segments compared, each with `segment_id`, `sol_range`, `length_m` and `selection_reason` | see example below |
| `notes` | string | yes | Honest summary, including any gap and its cause | `"<text>"` |

The landing point is the first `frame = SITE` row of `best_interp.csv`. Its sol is recorded as `n/a`, not as sol 0.

Example (metric values stay `null` until the code computes them):

```json
{
  "report_id": "<id>",
  "generated_at": "<timestamp>",
  "code_commit": "<commit hash>",
  "reference": {
    "file": "best_interp.csv",
    "release": "Release 16",
    "downloaded": "2026-11-15",
    "sha256": "58FBC62F2676195A00B40B2DA53A797A70284A8D2344B288C999D325B7CCB4CC",
    "sol_range": "0 to 1897"
  },
  "parameters": "<object copied from validation/params.json>",
  "metrics": { "end_point_error_m": null },
  "comparison_segments": [
    { "segment_id": "<id>", "sol_range": "<sol range>", "length_m": "<number>", "selection_reason": "<text>" }
  ],
  "notes": "<text>"
}
```

## Known limits

- The slope raster understates east-west slope by about 5% (see `slope.npy`). It was not recomputed.
- Points of interest were selected by eye from the hillshade. They are not CRISM detections, and spectral data are not used in route cost.
- The web page shows a static data snapshot, not live data.
- Validation compares routes with the PLACES reference. The MMGIS files are a cross-check only and are not used to set parameters.
