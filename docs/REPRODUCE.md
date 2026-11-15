# Reproduce

Commands are for Windows PowerShell and are run from the repository root.

## Requirements

- Python 3 and a virtual environment in `.venv`. The data pipeline was run with Python 3.13.14. Python 3.12 was not tested.
- Pinned packages are in `pipeline/requirements.txt` (data pipeline) and `routing/requirements.txt` (routing and tests). The shared packages have the same pins in both files. `scikit-image` is pinned to a release candidate (0.27.0rc1), which is a pre-release version. The latest stable release (0.26.0) was not tested.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r pipeline\requirements.txt -r routing\requirements.txt
```

## Windows line endings

Clone with line-ending conversion turned off:

```powershell
git clone -c core.autocrlf=false https://github.com/Nico8213/mars-eva-map-2026.git
```

With the default Git setting on Windows, text files are checked out with converted line endings. For example, `validation/data/best_interp.csv` is 8,684,070 bytes in the repository and 8,717,529 bytes after such a checkout. The SHA-256 check in `validation/run_validation.py` then stops with a mismatch. This does not mean the data is wrong.

## Data download

The pipeline reads two public USGS files. They are not stored in the repository. Download them from the pages below and place them at the paths given in `pipeline/README.md`. Both are CC0 1.0; please cite Fergason et al. (2020).

1. HiRISE DTM, `JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif` (version 006, 1 m/px, about 1.84 GB per `pipeline/README.md`): https://doi.org/10.5066/P9REJ9JN
2. CTX mosaic, `JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0.tif` (version 008, 6 m/px): https://doi.org/10.5066/P9GV1ND3

Already in the repository: the processed files in `data/processed/` (including `slope.npy` and the layer images), and the validation inputs in `validation/data/` (PLACES `best_interp.csv` and the MMGIS traverse snapshot). You can run routing, validation and the website without repeating the download.

## Pipeline

See `pipeline/README.md` for the steps, commands and outputs. The pipeline turns the two downloaded files into the processed files in `data/processed/`.

## Routing

See routing/README.md for how routes are produced. Route GeoJSON coordinates are grid metres, not longitude/latitude.

## Validation

Step 1, check the coordinate transform:

```powershell
.\.venv\Scripts\python.exe validation\check_transform.py
```

Output: `validation/out/check_transform.json`. This checks the coordinate transform only. It was made before the parameters were locked and is not the comparison with the Perseverance path.

Step 2, validate against the Perseverance traverse:

```powershell
.\.venv\Scripts\python.exe validation\run_validation.py
```

Output: `validation/out/report.json`

Note: this script was run once, after the parameters were locked (commit d1965fd). Do not edit `validation/params.json` and do not re-run it to tune results. Do not commit a re-generated `validation/out/report.json`. The committed report is the single run made after the parameters were locked (d1965fd). The result is a weak match, and the report records it as measured.

## Web preview

The website is static. To preview it locally, serve the `web/` folder:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --directory web
```

Open http://localhost:8000/ . The status line should read "Data loaded (static snapshot)". The published site is deployed by the GitHub Actions workflow in `.github/workflows/`.
