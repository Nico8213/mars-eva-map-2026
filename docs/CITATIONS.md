# Martian Map

Martian Map is a static web map prototype for planning an extravehicular activity (EVA) at Jezero crater, Mars. It was built for the NASA Space Apps Challenge 2026 challenge "Interplanetary Survival Guide: Martian Map". The map shows a slope layer, a hillshade and an optical image on one map, four points of interest, and a data card for each layer with its source, version, resolution, license and known issues.

## How to view the website

- Website: https://nico8213.github.io/mars-eva-map-2026/
- Video (30 s): TBD
- Local preview steps: see `docs/REPRODUCE.md`

## Data and known limits

- Terrain: USGS Mars 2020 Terrain Relative Navigation HiRISE DTM mosaic, version 006, 1 m/px (CC0 1.0; please cite Fergason et al., 2020).
- Optical layer: USGS CTX orthomosaic, 6 m/px, version 008. It is used as visual background only and does not affect route cost.
- Routing uses a slope constraint only. Spectral data (CRISM) are used as reference only. Points of interest were selected by eye from the hillshade; they are not CRISM detections.
- Known issue: the slope script uses 1 m spacing in both directions. East-west ground spacing is about 0.95 m, so east-west slope is understated by about 5%. The raster was not recomputed for v1.0.
- Coordinates: the DTM is equirectangular with true-scale latitude 0 on a Mars sphere of radius 3396190 m. The 18.4663 degree standard parallel of the PLACES map convention is not used.
- Validation reference: Mars 2020 Rover PLACES `best_interp.csv` (Release 16). The NASA/JPL MMGIS traverse files are used only as a cross-check. Validation parameters are locked in `validation/params.json` before any comparison is run.
- The web page shows a static data snapshot, not live data.

## Data sources

See `docs/CITATIONS.md` for every data source, version and license.

## Folder guide

- `data/`: Data folders. `data/processed/` holds the files the website and routing read (see `docs/INTERFACES.md`). Raw data is kept out of the repository (`local_only/` or `data/raw/`).
- `pipeline/`: Python scripts that process the raw data into processed files.
- `routing/`: Route planning scripts. Route output goes to `routing/out/`.
- `validation/`: Validation scripts. Validation output goes to `validation/out/`.
- `web/`: Static HTML and JavaScript website. `web/vendor/` holds Leaflet, and `web/public/data/` holds data files served to the site.
- `tools/`: Helper scripts.
- `docs/`: Project documents, including `INTERFACES.md`, `REPRODUCE.md` and `CITATIONS.md`. `docs/research/` holds research notes, and `docs/ai_log/` holds each team member's AI log.
- `.kiro/steering/`: Steering files that give project context to Kiro.
- `.github/workflows/`: GitHub Actions workflow files.

## Reproducing the results

See `docs/REPRODUCE.md`.

## Use of AI tools

AI tools were used during development. The logs are in `docs/ai_log/`.

## License

This project is licensed under the Apache License 2.0. See `LICENSE`. Third-party content is listed in `docs/CITATIONS.md`.
