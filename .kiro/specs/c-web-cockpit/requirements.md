# Requirements: c-web-cockpit

## Introduction

The web cockpit is a static website in `web/` that shows the Jezero crater study area as a flat image map. It displays three raster layers (F1), clickable points of interest (F2) and routes (F3). It uses Leaflet from `web/vendor/leaflet/` with `L.CRS.Simple` and `imageOverlay`. It has no Earth or planetary base map and no server.

Owner: C (`web/`, `tools/`, `.github/`). File formats follow `docs/INTERFACES.md` and are not changed by this spec.

Scope: F1, F2 and route display only. Data cards (F8), comparison (F10), validation (F7), environment (F9) and concept pages (F6) are out of scope.

## Glossary

- Cockpit: the single-page web app in `web/index.html`.
- Layer: one PNG listed in `layers.json`, drawn as an `imageOverlay`.
- POI: a point of interest from `poi.geojson`.
- Route: a GeoJSON `LineString` Feature from `route_<name>.geojson`.
- Extent: the bounding box of a layer in projected metres (easting/northing).
- Data root: `web/public/data/`.

## Requirements

### R1: Static hosting and local assets

**User story:** As a reviewer, I want the site to work from static files only, so that it can be hosted on GitHub Pages without a server.

Acceptance criteria:
1. THE Cockpit SHALL consist of static HTML, CSS and JavaScript files inside `web/`.
2. THE Cockpit SHALL load Leaflet only from `web/vendor/leaflet/` and SHALL NOT load any script, style, font or tile from a CDN or other external host.
3. THE Cockpit SHALL use relative URLs so it works when served from a sub-path (for example `https://<user>.github.io/<repo>/`).
4. THE Cockpit SHALL read all data from the Data root and SHALL NOT contain hard-coded layer, POI or route data in code.
5. THE Cockpit SHALL need no build step.

### R2: Map without a base map

**User story:** As a user, I want a plain image map in metre coordinates, so that no Earth map is shown for a Mars site.

Acceptance criteria:
1. THE Cockpit SHALL create the map with `crs: L.CRS.Simple`.
2. THE Cockpit SHALL NOT add any `tileLayer`, OpenStreetMap layer or other Earth or planetary base map.
3. THE Cockpit SHALL map easting to Leaflet `lng` (x) and northing to Leaflet `lat` (y), so that northing increases upward on screen.
4. WHEN the layer list has loaded, THE Cockpit SHALL fit the initial view to the union of all layer extents.
5. THE Cockpit SHALL show a scale or coordinate readout in metres, and SHALL show the CRS name as "TBD" or as read from data, and SHALL NOT invent a CRS name.

### R3: Layers with toggle and opacity (F1)

**User story:** As a user, I want to switch each layer on and off and change its opacity, so that I can compare terrain, optical and spectral views.

Acceptance criteria:
1. THE Cockpit SHALL load `layers/layers.json` from the Data root and create one `imageOverlay` per entry, using `file` (relative to `layers/`) as the image URL and `extent` as the bounds.
2. THE Cockpit SHALL show at least three layers when `layers.json` lists three entries.
3. THE Cockpit SHALL show one control row per layer with the layer `name`, a checkbox to toggle visibility and a slider for opacity from 0 to 1.
4. WHEN the user clears a layer checkbox, THE Cockpit SHALL remove that overlay from the map. WHEN the user selects it again, THE Cockpit SHALL add it back with its current opacity.
5. WHEN the user moves an opacity slider, THE Cockpit SHALL update that overlay opacity immediately, without reloading the image.
6. THE Cockpit SHALL set all layers visible with a default opacity of 0.7 at start.
7. THE Cockpit SHALL keep the order of layers from `layers.json` as the drawing order, and the order SHALL NOT change when layers are toggled.
8. IF a layer image fails to load, THEN THE Cockpit SHALL show an error message naming the layer and SHALL keep the other layers working.

### R4: POI click (F2)

**User story:** As a user, I want to click a point of interest and see its name and type, so that I know what is there.

Acceptance criteria:
1. THE Cockpit SHALL load `poi.geojson` from the Data root and draw one marker per `Point` feature at `[easting_m, northing_m]`.
2. THE Cockpit SHALL draw POI markers as vector circle markers and SHALL NOT depend on Leaflet default marker images.
3. WHEN the user clicks a POI, THE Cockpit SHALL open a popup that shows `name` and `type`.
4. THE popup SHALL also show `source` and `evidence`, because `INTERFACES.md` says `evidence` is shown on click.
5. THE Cockpit SHALL insert all text from data with `textContent` or an equivalent safe method, and SHALL NOT insert data strings as HTML.
6. IF `poi.geojson` fails to load, THEN THE Cockpit SHALL show an error message and keep the layers and routes working.
7. THE Cockpit SHALL allow the POI group to be switched on and off.

### R5: Route display (F3)

**User story:** As a user, I want to see routes drawn on the map with their basic facts, so that I can read the proposed path.

Acceptance criteria:
1. THE Cockpit SHALL load route files listed in `routes/index.json` from the Data root, and SHALL draw each `LineString` as a polyline using `[easting_m, northing_m]` coordinates.
2. WHEN the user clicks a route, THE Cockpit SHALL show `name`, `length_m`, `max_slope_deg`, `slope_threshold_deg`, `data_used`, `start_poi` and `end_poi`.
3. THE Cockpit SHALL draw routes above the layers and below or equal to the POI markers.
4. THE Cockpit SHALL allow the route group to be switched on and off.
5. THE Cockpit SHALL display numbers exactly as stored and SHALL NOT compute route length or slope in the browser.
6. IF a route file fails to load, THEN THE Cockpit SHALL show an error message naming the file and keep the rest working.
7. IF a route property is missing, THEN THE Cockpit SHALL show "n/a" for that field.

### R6: Data conforming to INTERFACES.md

**User story:** As a team member, I want placeholder data in the real formats, so that real data from A and B can replace it with no code change.

Acceptance criteria:
1. THE Data root SHALL contain three placeholder PNG layers (`terrain.png`, `optical.png`, `spectral.png`) under `layers/`, each RGBA and semi-transparent.
2. `layers/layers.json` SHALL be an array of objects with `name`, `file`, `extent` (`min_easting_m`, `min_northing_m`, `max_easting_m`, `max_northing_m`) and `data_card_id`, with numeric extent values.
3. `poi.geojson` SHALL be a `FeatureCollection` of `Point` features, each with `id`, `name`, `type`, `source` (`"CRISM"` or `"optical"`) and `evidence`, plus `selection_rule` where used.
4. Each route file SHALL be a GeoJSON `Feature` with a `LineString` and the properties `name`, `start_poi`, `end_poi`, `length_m`, `max_slope_deg`, `slope_threshold_deg`, `data_used`, `cost_function` and `generated_from`.
5. All placeholder text SHALL be marked "DUMMY" or "placeholder" so no one mistakes it for real data.
6. All JSON files SHALL be UTF-8 with 2-space indentation, and every file SHALL be under 50 MB.
7. THE Cockpit SHALL treat data coordinates as projected metres in the common CRS defined by `INTERFACES.md`, and SHALL NOT reproject.

### R7: Language and accessibility

**User story:** As a user, I want a readable, keyboard-usable interface in English.

Acceptance criteria:
1. ALL visible text, code comments and identifiers SHALL be in English.
2. EVERY control SHALL have a visible text label or an `aria-label`.
3. THE layer checkboxes and sliders SHALL be reachable and operable with the keyboard.
4. THE Cockpit SHALL show a visible note that the displayed data is placeholder data while the files are marked DUMMY.

## Out of scope

- Data cards panel (F8), comparison (F10), validation (F7), environment layer (F9), concept pages (F6).
- Reprojection, tiling, server code, live data.
- Changing any format in `docs/INTERFACES.md`.

## Open questions

- `INTERFACES.md` does not define where `layers.json` lives relative to the data root or how routes are listed. This spec assumes `layers/layers.json` and an added `routes/index.json`. Confirm with A and B in the group chat before the real data arrives.
- CRS name and POI coordinate convention are TBD in `INTERFACES.md` (PRD section 12.6). The Cockpit assumes `[easting_m, northing_m]`.
