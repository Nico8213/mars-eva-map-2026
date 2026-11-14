# Martian Map

## Summary (3 sentences)
Martian Map is a cockpit planning display for an extravehicular activity (EVA) at Jezero crater, combining terrain, optical and spectral data on one map. Each layer will show its source, version, resolution, license and known issues, so the crew will be able to see how far the data can be trusted. The team plans to check its route against a real Perseverance traverse and will report the result as measured, whatever it shows.

## The problem
Mars Trek and the USGS-NASA planetary mapping programs are useful for regional and global views. They are not designed for the very local detail an astronaut needs for a single surface walk. Before an EVA, a crew needs one map that overlays terrain, optical imagery and mineral information, and that says where to go, how to get there and why.

## Our solution
The cockpit planning display (the only part of the three-device concept the team plans to build fully) will show the Jezero area with at least three layers that will be switchable on and off and adjustable for transparency: terrain, optical imagery and spectral data. Points of interest (POI) from CRISM and optical imagery will mark candidate science sites, and clicking a point will show the evidence behind it. A route planner will start and end at POIs and will avoid steep slopes above a threshold; the threshold and cost function are to be documented. Clicking any layer will open a data card with its source mission, instrument, version, resolution, license, known issues and the decision it affects. A comparison view will show how each dataset changes the route. The tablet and helmet HUD will appear only as concept pages.

## How we use NASA data
- HiRISE DTM v003, 1 m/px, Jezero area (terrain; slope is derived from this). Status: candidate. Link: TBD
- CTX orthorectified mosaic, 5 m/px (optical). Status: candidate. Link: TBD
- HiRISE orthorectified image, 0.25 m/px (optical). Status: candidate. Link: TBD
- CRISM hydrous mineral detections, accessed through JMARS (spectral; key input for POIs). Product page, version, resolution and license: TBD
- Perseverance traverse, M20_traverse.json and M20_waypoints.json, snapshot 2026-10-11 (sol 1980). Used only for validation. Status: checked by the team, not yet reviewed by a second person. Link: TBD
- Ancillary (environment reference panel): radiation and dust storm sources are TBD. Not used in route cost.

## Why it matters
The best-data direction focuses on making space data easier to use and putting it to a specific use. Martian Map treats data provenance as a core feature: every layer will carry its source and version, a data card will explain known problems, and a comparison view will show where data changed a decision instead of only decorating the map. The steps from raw data to web layers are to be written up as a reproducibility note with a fixed snapshot list, so others can rebuild the layers. Route results and validation numbers will be added only after the program computes them.

## Try it
- Website: TBD
- Source code: https://github.com/Nico8213/mars-eva-map-2026
- Video (30 s): TBD

## AI tools used
TBD

## Team
- Nicole: route planning (F3), validation (F7)
- Charles: layer display and data cards (F1, F8)
- Xin En: POI and data cards (F2, F8), environment reference panel (F9)
- Daniel: project page and demo video (F4)
- Austin: concept pages for tablet and HUD (F6), reproducibility note draft (F11)
- Veann: comparison route (F10), environment reference panel (F9)
