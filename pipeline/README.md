# Data pipeline

This folder holds the Python scripts that turn the cropped HiRISE DTM into the slope, layer, point-of-interest and data-card files used by routing and the web app. Written 2026-11-15 from the scripts in this folder, `pipeline/config.json` and `data/processed/sources.md`.

## 1. Purpose

The pipeline produces these files:

| File | Written by | Content |
| --- | --- | --- |
| `data/raw/cropped_dtm.tif` | `step1_crop_dtm.py` | Crop of the HiRISE DTM, 4000 x 4000 px at 1 m/px |
| `data/processed/slope.npy` | `step2_slope.py` | Slope in degrees, float32, same grid as the crop |
| `data/processed/grid.json` | `step2_slope.py` | Grid metadata: source product, version, DOI, CRS, top-left corner, pixel size, known issue |
| `data/processed/layers/slope.png` | `step3_layers.py` | 8-bit grayscale slope image. Slope from 0 to 45 degrees maps to 0 to 255; steeper values clip to 255 |
| `data/processed/layers/hillshade.png` | `step3_layers.py` | 8-bit grayscale hillshade, azimuth 315 degrees, altitude 45 degrees |
| `data/processed/layers/layers.json` | `step3_layers.py`, `step6_ctx.py` | Layer manifest: name, file, extent in degrees, data card ID |
| `data/processed/layers/ctx.png` | `step6_ctx.py` | 8-bit grayscale CTX crop with a 2 to 98 percentile stretch; nodata is transparent |
| `data/processed/poi.geojson` | `step4_poi.py` | Points of interest in longitude and latitude |
| `data/processed/data_cards.json` | `step5_cards.py` | Data cards for the HiRISE DTM and the CTX mosaic |
| `data/raw/ctx_vs_hillshade_check.png` | `step6_ctx.py` | Side-by-side check image (CTX and hillshade). Not an app layer |

## 2. Inputs

Raw inputs are not in the repository. Keep them in `local_only/`.

The paths in `pipeline/config.json` are relative to the repository root. The config points to `../local_only/`, which is a folder next to the repository (for example `C:\SpaceApps2026\local_only\`), not a folder inside it. Place the files at the paths below, or change the paths in `config.json`. On the machine that ran the pipeline, the folder is C:\SpaceApps2026\local_only\ and holds hirise_raw\ and ctx_raw\.

| Input | Product name | Version | DOI | Config key and path |
| --- | --- | --- | --- | --- |
| HiRISE DTM | `JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40`, Mars 2020 Terrain Relative Navigation HiRISE DTM Mosaic (Jezero), USGS Astrogeology Science Center | 006, 1 m/px (from `sources.md`) | 10.5066/P9REJ9JN | `source_dtm`: `../local_only/hirise_raw/JEZ_hirise_soc_006_DTM_1m.tif` (1,839,545,409 bytes, from `sources.md`) |
| CTX orthomosaic | `JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0` (from `step5_cards.py`) | 008, 6 m/px (from `step5_cards.py`) | 10.5066/P9GV1ND3 (from `step5_cards.py`) | `source_ctx`: `../local_only/ctx_raw/JEZ_ctx_6m.tif` |

The HiRISE crop uses the window in `config.json`, in projected metres of the native CRS: west 4587600.0, east 4591600.0, south 1092600.0, north 1096600.0. The native CRS is Equirectangular Mars 2000 Sphere IAU, standard parallel 0 (from `grid.json`).

`JEZ_ctx_6m.tif` is a local, cropped copy of the USGS mosaic `JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0`.

## 3. Setup

Use Python 3.12, as set in the project technical rules. The scripts import `numpy`, `rasterio` and `Pillow` (imported as `PIL`).

Install the pinned packages from `pipeline/requirements.txt` with `pip install -r pipeline/requirements.txt`, as shown below.

Windows (PowerShell), from the repository root:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r pipeline/requirements.txt
```

Mac (Terminal), from the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r pipeline/requirements.txt
```

The usage lines in the scripts call the interpreter directly (`.venv/Scripts/python.exe` on Windows), so activation is optional on Windows. On Mac, use `.venv/bin/python` in place of `.venv/Scripts/python.exe`.

## 4. Run order

Run all commands from the repository root, in this order. Each step reads the outputs of the steps before it. Each script prints the files it wrote.

Windows (PowerShell):

```powershell
.venv/Scripts/python.exe pipeline/step1_crop_dtm.py
.venv/Scripts/python.exe pipeline/step2_slope.py
.venv/Scripts/python.exe pipeline/step3_layers.py
.venv/Scripts/python.exe pipeline/step4_poi.py
.venv/Scripts/python.exe pipeline/step6_ctx.py
.venv/Scripts/python.exe pipeline/step5_cards.py
```

Mac (Terminal):

```bash
.venv/bin/python pipeline/step1_crop_dtm.py
.venv/bin/python pipeline/step2_slope.py
.venv/bin/python pipeline/step3_layers.py
.venv/bin/python pipeline/step4_poi.py
.venv/bin/python pipeline/step6_ctx.py
.venv/bin/python pipeline/step5_cards.py
```

| Step | Reads | Writes |
| --- | --- | --- |
| 1. `step1_crop_dtm.py` | `pipeline/config.json`; the HiRISE DTM at `source_dtm` | `data/raw/cropped_dtm.tif` |
| 2. `step2_slope.py` | `data/raw/cropped_dtm.tif` | `data/processed/slope.npy`, `data/processed/grid.json` |
| 3. `step3_layers.py` | `data/processed/slope.npy`, `data/raw/cropped_dtm.tif` | `data/processed/layers/slope.png`, `hillshade.png`, `layers.json` |
| 4. `step4_poi.py` | `pipeline/poi_manual.csv`, `grid.json`, `layers/layers.json` | `data/processed/poi.geojson` |
| 5. `step6_ctx.py` | The CTX mosaic at `source_ctx`; `data/raw/cropped_dtm.tif` (CRS check); `layers/hillshade.png`; `layers/layers.json` | `data/processed/layers/ctx.png`, `layers.json` (adds the CTX entry), `data/raw/ctx_vs_hillshade_check.png` |
| 6. `step5_cards.py` | `grid.json`, `layers/layers.json`, `data/processed/sources.md` | `data/processed/data_cards.json` |

Order notes:

- Step 6 must run after step 3. Step 3 rewrites `layers.json` without the CTX entry, so run step 6 again after every new run of step 3.
- Step 4 needs `grid.json` from step 2 and `layers.json` from step 3. Its extent check uses the first layer in `layers.json`, which is the slope layer.
- Step 5 runs last, after step 6, because it reads `layers.json`.
- Step 5 stops if `sources.md` no longer contains the known-issue phrase "stereo DTM artifacts and seams".
- Step 6 stops before writing anything if the CTX CRS differs from the cropped DTM CRS.

## 5. Known limitations

- **East-west slope is underestimated by up to about 5 percent.** The gradient uses 1 m spacing in both directions. At latitude about 18.5 degrees, one east-west pixel spans about 0.95 m on the ground. The correction is not applied, so the routing validation inputs stay fixed (see `sources.md`).
- **Points of interest are selected by eye** from `hillshade.png`. None comes from a CRISM detection. All four rows in `poi_manual.csv` have source `hillshade` (the image the point was selected from, per INTERFACES.md).
- EPSG:49900 is not in the PROJ database on the machine used to build the data, so the scripts used the sphere fallback (+proj=longlat +R=3396190 +no_defs, radius 3396190 m).
- **`slope.npy` is about 64 MB** (4000 x 4000 float32, 64,000,128 bytes). It stays in `data/processed/` so routing can run without the 1.84 GB DTM. This file is above the 50 MB per-file limit in the project technical rules. The file is committed in data/processed/ and stays in the repository because the validation report references it by hash (per Nicole). GitHub warned on push that it is 61.04 MiB, above the recommended 50 MB, but below the 100 MB hard limit.
- **DTM known issue:** stereo DTM artifacts and seams (from `sources.md`).
- **CTX known issues** (from `step5_cards.py`): individual CTX images have an average horizontal displacement of 9.6 m. A small gap in the northwest corner of the full mosaic was filled with an image orthorectified to an HRSC DTM.

## 6. Licenses

- **HiRISE DTM:** CC0 1.0 Universal (USGS data release page, checked 2026-11-14). Cite the authors: Fergason, R. L., et al. (2020), DOI 10.5066/P9REJ9JN. The USGS product page also asks users to cite the authors. The full entry is in `docs/CITATIONS.md`.
- **CTX mosaic:** CC0 1.0 Universal per the USGS data release page (DOI 10.5066/P9GV1ND3), checked 2026-11-14, downloaded 2026-11-14. Cite the authors; see `docs/CITATIONS.md`.
- **Python packages** (numpy, rasterio, Pillow):
  - numpy 2.5.4: BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0;
  - rasterio 1.5.2: BSD-3-Clause;
  - Pillow 13.0.0: MIT-CMU.

  scikit-image 0.27.0rc1 (a pre-release; latest stable is 0.26.0, not tested) and scipy 1.18.1 declare the classifier 'License :: OSI Approved :: BSD License'; see each project's LICENSE for the exact BSD variant.

  See `docs/CITATIONS.md`.
- **Pipeline code:** Apache 2.0, as stated in the repository `LICENSE`.
