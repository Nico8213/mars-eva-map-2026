# Martian Map

Martian Map is a map prototype for Mars extravehicular activity (EVA) at Jezero crater, built for NASA Space Apps Challenge 2026. It will overlay terrain, optical and spectral data on one map, and each layer will show its source, version, known issues and the decisions it affects. The app will also show how the data changes route choices.

## How to view the website

- Website: TBD
- Video (30 s): TBD

Local preview steps: TBD

## Data sources

See `docs/CITATIONS.md` for every data source, version and license.

## Folder guide

- `data/`: Data folders. `data/processed/` holds the files the website and routing read (see `docs/INTERFACES.md`). Raw data is kept out of the repository (`local_only/` or `data/raw/`).
- `pipeline/`: Python scripts that process the raw data into processed files.
- `routing/`: Route planning scripts. Route output goes to `routing/out/`.
- `validation/`: Validation scripts. Validation output goes to `validation/out/`.
- `web/`: Static HTML and JavaScript website. `web/vendor/` holds Leaflet, and `web/public/data/` holds data files served to the site.
- `tools/`: Helper scripts.
- `docs/`: Project documents, including `SUBMISSION.md`, `INTERFACES.md`, `REPRODUCE.md` and `CITATIONS.md`. `docs/research/` holds research notes, and `docs/ai_log/` holds each team member's AI log.
- `.kiro/steering/`: Steering files that give project context to Kiro.
- `.github/workflows/`: GitHub Actions workflow files.

## Reproducing the results

See `docs/REPRODUCE.md`.

## License

This project is licensed under the Apache License 2.0. See `LICENSE`. Third-party content is listed in `docs/CITATIONS.md`.
