# Tasks: c-web-cockpit

- [x] 1. Create placeholder data in `web/public/data/` (R6)
  - [x] 1.1 Three semi-transparent RGBA PNGs: `layers/terrain.png`, `layers/optical.png`, `layers/spectral.png`
  - [x] 1.2 `layers/layers.json` with three entries and numeric extents
  - [x] 1.3 `poi.geojson` with three Point features
  - [x] 1.4 `routes/route_ea-01.geojson` and `routes/index.json`
  - _Requirements: R6_

- [ ] 2. Page shell and styles (R1, R7)
  - [ ] 2.1 Replace `web/index.html` with the header, side panel, map container and status region
  - [ ] 2.2 Load `vendor/leaflet/leaflet.css` and `leaflet.js` with relative paths, no CDN
  - [ ] 2.3 Add `css/cockpit.css` for layout, focus outlines and the placeholder-data notice
  - _Requirements: R1, R7_

- [ ] 3. Data helpers and map setup (R1, R2)
  - [ ] 3.1 `js/data.js`: `DATA_ROOT`, `loadJson`, `toLatLng`, `extentToBounds`, `showError`
  - [ ] 3.2 `js/main.js`: create the map with `L.CRS.Simple`, no tile layer, create panes, metre scale and E/N readout, show "CRS: TBD"
  - [ ] 3.3 Fit the view to the union of all layer extents
  - _Requirements: R1, R2_

- [ ] 4. Layers with toggle and opacity (R3)
  - [ ] 4.1 `js/layers.js`: create one `imageOverlay` per `layers.json` entry in a fixed pane order
  - [ ] 4.2 Build the checkbox and opacity slider row for each layer with labels
  - [ ] 4.3 Default visible at opacity 0.7, show an error on image load failure
  - _Requirements: R3, R7_

- [ ] 5. POI click (R4)
  - [ ] 5.1 `js/poi.js`: draw circle markers from `poi.geojson` using `coordsToLatLng`
  - [ ] 5.2 Popup with name, type, source and evidence using `textContent` only
  - [ ] 5.3 POI list buttons in the side panel for keyboard access, and a group toggle
  - _Requirements: R4, R7_

- [ ] 6. Route display (R5)
  - [ ] 6.1 `js/routes.js`: read `routes/index.json`, load each route with `Promise.allSettled`
  - [ ] 6.2 Draw polylines above layers, popup with route properties, "n/a" for missing fields
  - [ ] 6.3 Group toggle for routes
  - _Requirements: R5_

- [ ] 7. Manual verification
  - [ ] 7.1 Serve `web/` locally and confirm no external network requests
  - [ ] 7.2 Check toggle, opacity, POI popup, route popup and error paths
  - [ ] 7.3 Check keyboard use of all controls
  - [ ] 7.4 Confirm the deploy workflow publishes `web/` with the data and vendor files
  - _Requirements: R1 to R7_

- [ ] 8. Housekeeping
  - [ ] 8.1 Add the Leaflet entry (name, version, license BSD-2-Clause) to `docs/CITATIONS.md` and ask D to merge it, because `docs/` belongs to D
  - [ ] 8.2 Add one line to the C AI log (`docs/ai_log/C-charles.md`)
  - [ ] 8.3 Commit with the `[C]` prefix in English
  - _Requirements: R1_
