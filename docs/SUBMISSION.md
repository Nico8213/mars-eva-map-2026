# Martian Map

## Summary (3 sentences)
Martian Map will be a cockpit planning display for an extravehicular activity (EVA) at Jezero crater, combining terrain, optical and spectral data on one map. Each layer will show its source, version, resolution, license and known issues, so the crew can see how far the data can be trusted. The team plans to check its route against a real Perseverance traverse and will report the result as measured, whatever it shows.

## The problem
Mars Trek and the USGS-NASA planetary mapping programs work well for regional and global views, but they are not designed for the very local detail an astronaut needs on a single surface walk. Before an EVA, a crew needs one map that overlays terrain, optical imagery and mineral information, and shows where to go, how to get there and why.

## Our solution
We will build one cockpit planning display for the Jezero area; the tablet and helmet HUD will appear only as concept pages. It will offer at least three layers (terrain, optical imagery and spectral data) that can be switched on and off and adjusted for transparency. Points of interest from CRISM and optical imagery will mark candidate science sites, and a route planner will connect them while avoiding slopes above a documented threshold. Clicking any layer will open a data card with its source, version, resolution, license, known issues and the decision it affects, and a comparison view will show how each dataset changes the route.

## How we use NASA data
- HiRISE DTM v003, 1 m/px, Jezero area (terrain; slope is derived from this). Status: candidate. Link: TBD
- CTX orthorectified mosaic, 5 m/px (optical). Status: candidate. Link: TBD
- HiRISE orthorectified image, 0.25 m/px (optical). Status: candidate. Link: TBD
- CRISM hydrous mineral detections, accessed through JMARS (spectral; key input for POIs). Product page, version, resolution and license: TBD
- Perseverance traverse, M20_traverse.json and M20_waypoints.json, snapshot 2026-10-11 (sol 1980). Used only for validation. Status: checked by the team, not yet reviewed by a second person. Link: TBD
- Ancillary (environment reference panel): radiation and dust storm sources are TBD. Not used in route cost.

## Why it matters
The project aims to make space data easier to use and to put it to a specific use. Martian Map treats data provenance as a core feature: every layer will carry its source and version, a data card will explain known problems, and a comparison view will show where data changed a decision instead of only decorating the map. A reproducibility note with a fixed snapshot list will let others rebuild the layers from raw data. Route results and validation numbers will be added only after the program computes them.

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