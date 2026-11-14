# AI log: Charles (C)

Add one line every time an AI tool helps you. Write in English.
Format: date time | tool and model | what you asked | what it did | how you checked it

2026-11-13 | Kiro (Auto) | Create spec c-web-cockpit and dummy data in web/public/data | Wrote requirements, design and tasks in .kiro/specs/c-web-cockpit and generated 3 PNG layers, layers.json, poi.geojson and one route | Parsed all JSON, checked PNG headers (400x400 RGBA) against INTERFACES.md fields
2026-11-13 | Kiro (Auto) | Start task 2 of c-web-cockpit | Rewrote web/index.html as the page shell and added web/css/cockpit.css | Checked the Leaflet paths exist; not yet opened in a browser2026-11-13 | Kiro (Auto) | Start task 3 of c-web-cockpit | Added web/js/data.js and web/js/main.js (map with L.CRS.Simple, panes, scale, E/N readout, fit to layer extents) and linked them in index.html | Not run in a browser; no Node available for a syntax check
2026-11-13 | Kiro (Auto) | Start task 4 of c-web-cockpit | Added web/js/layers.js (imageOverlay per layer, checkbox and opacity slider rows) and linked it in index.html | Loaded the page in headless Edge via a local server and checked the DOM: 3 overlays, 3 control rows, no error messages; toggle and slider not clicked
2026-11-13 | Kiro (Auto) | Start task 5 of c-web-cockpit | Added web/js/poi.js (circle markers, popup with name/type/source/evidence, group toggle, keyboard POI list); main.js now fires cockpit:map-ready after the view is set | Ran a temporary script in headless Edge: 3 markers, popup text correct, layer toggle, opacity, POI toggle and list button all worked, 0 errors; temp files removed
