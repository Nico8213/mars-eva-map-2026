# Design: c-web-cockpit

## Overview

A single static page. Plain JavaScript, no build step, no framework. Leaflet 
comes from `web/vendor/leaflet/`. The map uses `L.CRS.Simple`. Layers are `imageOverlay` objects. POIs and routes are vector layers built from GeoJSON.

## File layout

```
web/
  index.html                 page shell, controls panel, map container
  css/cockpit.css            layout and control styles
  js/
    main.js                  entry point: loads data, builds map and panels
    data.js                  fetch helpers and data-root URL
    layers.js                imageOverlay creation and layer control panel
    poi.js                   POI markers and popups
    routes.js                route polylines and popups
  vendor/leaflet/            Leaflet (already present, no CDN)
  public/data/
    layers/layers.json
    layers/terrain.png
    layers/optical.png
    layers/spectral.png
    poi.geojson
    routes/index.json        list of route file names (cockpit-only helper)
    routes/route_ea-01.geojson
```

Scripts are plain `<script>` files (no ES module bundler) loaded after `leaflet.js`. ES modules are also fine on GitHub Pages, but plain scripts also work when opening the page from a simple local server.

Local preview: `python -m http.server` inside `web/`. `fetch` does not work from `file://`, so a local server is required.

## Coordinate handling

Data uses projected metres: `x = easting_m`, `y = northing_m`. `L.CRS.Simple` uses `LatLng(lat, lng)` where `lat` is the vertical axis. Mapping:

| Data | Leaflet |
|---|---|
| easting_m | lng |
| northing_m | lat |

Helper in `data.js`:

```js
// Convert [easting_m, northing_m] to a Leaflet LatLng for L.CRS.Simple.
function toLatLng(coord) { return L.latLng(coord[1], coord[0]); }

// Convert a layers.json extent to Leaflet bounds [[south, west], [north, east]].
function extentToBounds(e) {
  return [[e.min_northing_m, e.min_easting_m], [e.max_northing_m, e.max_easting_m]];
}
```

GeoJSON loading uses `L.geoJSON(data, { coordsToLatLng: toLatLng, ... })` so no reprojection takes place. Northing increases upward, matching the north-up PNG rows described in `INTERFACES.md`.

## Map setup

```js
const map = L.map('map', { crs: L.CRS.Simple, minZoom: -4, maxZoom: 4, zoomSnap: 0.25 });
// No tileLayer is added.
map.fitBounds(unionOfExtents);
```

- `minZoom` and `maxZoom` are adjusted after the extent is known so the map is not lost.
- A `mousemove` handler shows `E`/`N` in metres in a small readout. A `L.control.scale` with `imperial: false` is used because one map unit equals one metre.
- The CRS label reads "CRS: TBD" until `grid.json` or data supplies it. The cockpit does not invent a name.

## Components

### Data loader (`data.js`)

- `DATA_ROOT = 'public/data/'` (relative, works under a sub-path).
- `loadJson(path)` wraps `fetch`, checks `response.ok`, returns parsed JSON, throws an error with the path on failure.
- Errors are reported to the status area via `showError(message)`; the page never throws unhandled.

### Layer manager (`layers.js`)

- Input: array from `layers/layers.json`.
- For each entry creates `L.imageOverlay(DATA_ROOT + 'layers/' + file, extentToBounds(extent), { opacity: 0.7, alt: name, interactive: false })` and keeps `{ name, overlay, visible }`.
- Each overlay gets a Leaflet pane z-index from list order (`zIndex` option via `className` or a per-layer pane `layer-0`, `layer-1`, ...) so the drawing order is stable regardless of toggle order.
- UI row per layer (built with DOM APIs):
  - `<input type="checkbox" id="layer-i">` plus `<label for>` with the name
  - `<input type="range" min="0" max="1" step="0.05">` with `aria-label="Opacity of <name>"`
- Toggle: `map.addLayer` / `map.removeLayer`. Opacity: `overlay.setOpacity(value)`.
- Image load errors: `overlay.on('error', ...)` calls `showError('Layer image failed: <name>')`.

### POI layer (`poi.js`)

- `L.geoJSON(poi, { coordsToLatLng, pointToLayer })`. `pointToLayer` returns `L.circleMarker` (radius 7, fixed colour per `source`: CRISM and optical). No default marker PNG is used.
- Popup built as DOM nodes: title with `name`, a row `Type: <type>`, `Source: <source>`, `Evidence: <evidence>`. All strings via `textContent`.
- Keyboard: circle markers are SVG paths and are not focusable by default. A POI list in the side panel (button per POI, click calls `map.setView` and opens the popup) provides the keyboard path.

### Route layer (`routes.js`)

- Loads `routes/index.json` (array of file names), then each file with `Promise.allSettled` so one failure does not stop the others.
- Each route: `L.geoJSON(feature, { coordsToLatLng, style })` with a bright line weight 4 on a darker casing for contrast on all three layers.
- Click popup shows `name`, `length_m` (m), `max_slope_deg`, `slope_threshold_deg`, `data_used` (joined), `start_poi`, `end_poi`. Missing field shows `n/a`. Numbers are printed as stored.
- Draw order: custom panes, `layers` (z 200 to 299), `routes` (z 450), `poi` (z 460).

### Group toggles

Checkbox rows "Points of interest" and "Routes" add or remove the whole `L.layerGroup`.

## Page structure and accessibility

```
<header>  title + "Placeholder data" notice
<aside>   Layers fieldset, Overlays fieldset, POI list, status/error region (aria-live="polite")
<main id="map" role="application" aria-label="Map of the study area">
```

- Every control has a `<label>` or `aria-label`.
- Colour is not the only cue: POI source is also named in the popup and the POI list.
- Visible focus style is kept (Leaflet default plus CSS outline on buttons).
- All text is English.

## Data files

Dummy dataset used until A and B deliver real files. Study area is a 1000 m by 1000 m square, easting 0 to 1000, northing 0 to 1000, in the placeholder CRS (name TBD).

| File | Content |
|---|---|
| `layers/terrain.png`, `optical.png`, `spectral.png` | 400 x 400 RGBA, semi-transparent, 50 px white grid lines, different pattern per layer |
| `layers/layers.json` | 3 entries, extent 0..1000 in both axes, `data_card_id` values `card-terrain-dummy`, `card-optical-dummy`, `card-spectral-dummy` |
| `poi.geojson` | 3 Points: `poi-001` (200, 200) optical, `poi-002` (780, 720) CRISM, `poi-003` (300, 800) CRISM |
| `routes/route_ea-01.geojson` | LineString from `poi-001` to `poi-002`, 6 points, `length_m` 794.7 (sum of segment lengths) |
| `routes/index.json` | `["route_ea-01.geojson"]` |

All strings that are not real data start with "DUMMY". `data_card_id` values point to cards that do not exist yet because `data_cards.json` is out of scope here.

### Conformance with INTERFACES.md

- `layers.json`: fields `name`, `file`, `extent{4 keys}`, `data_card_id` all present, extent values are numbers.
- `poi.geojson`: Point features, `[easting_m, northing_m]`, properties `id`, `name`, `type`, `source`, `evidence`, `selection_rule`.
- Route: Feature with LineString and all nine required properties. `length_m` matches the geometry. `data_used` uses layer ids `terrain` and `spectral`.
- Layer `file` is relative to `layers/`, as defined.

### Deviations and assumptions

- `routes/index.json` is not in `INTERFACES.md`. A static host cannot list a folder, so the cockpit needs a list. Proposed to the group; B should add the route name when exporting.
- `layers.json` sits in `layers/` next to the PNGs. `INTERFACES.md` names the files together but not the exact location.

## Error handling

| Failure | Behaviour |
|---|---|
| `layers.json` not loadable | Error message, no layers, map shows empty grid area; POIs and routes still load |
| One layer PNG missing | Message naming the layer, other layers work |
| `poi.geojson` not loadable | Message, layers and routes still work |
| A route file not loadable | Message naming the file, other routes work |
| Missing route property | "n/a" shown |

## Testing approach

No automated test framework is added (not requested). Manual checks:

1. Serve `web/` with `python -m http.server` and open the page. No network request leaves localhost (browser dev tools, Network tab).
2. Three layers show, each toggles and changes opacity.
3. Clicking each POI shows name and type.
4. Clicking the route shows its properties.
5. Rename a PNG temporarily to confirm the error message and that other layers continue.
6. Keyboard only: Tab to every control, POI list button opens popup.

## Requirements traceability

| Requirement | Covered by |
|---|---|
| R1 | File layout, relative `DATA_ROOT`, no CDN |
| R2 | Map setup, coordinate handling |
| R3 | Layer manager |
| R4 | POI layer |
| R5 | Route layer |
| R6 | Data files, conformance |
| R7 | Page structure and accessibility |

## Update 2026-11-13: real layers.json from A

The first real `layers.json` differs from `INTERFACES.md`, so the cockpit accepts both forms:

| Item | INTERFACES.md | Real file from A | Cockpit |
|---|---|---|---|
| `extent` keys | `min_easting_m`, `min_northing_m`, `max_easting_m`, `max_northing_m` | `west`, `east`, `south`, `north` (degrees, lon/lat) | Both accepted (`Cockpit.extentToBounds`) |
| `file` | relative to `layers/` | `layers/slope.png` (relative to the data folder) | Both accepted (`Cockpit.layerUrl`) |

- With degree extents the map unit is degrees. The readout shows Lon/Lat, and the scale control is left out because it measures in map units and would print wrong distances.
- The zoom range is set wide at start and narrowed to fit zoom -2 / +4 after the layers load.
- No reprojection is done. The dummy POI and route are in metres (0 to 1000) and do not line up with the degree extent until A and B deliver real files in the same unit as the layers.
- Ask A to confirm the unit (degrees or metres) and to align `layers.json` with `INTERFACES.md`.
