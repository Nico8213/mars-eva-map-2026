# Data sources



## Terrain: Mars 2020 TRN HiRISE DTM Mosaic (Jezero)

- Local file: JEZ_hirise_soc_006_DTM_1m.tif (1,839,545,409 bytes)

- Official product name: JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40 (matches the Online File Link on the USGS page)

- Provider: USGS Astrogeology Science Center

- DOI: 10.5066/P9REJ9JN

- Version: 006 (taken from the file name)

- Resolution: 1 m/px

- Downloaded: 2026-11-14

- Native CRS: Equirectangular Mars 2000 Sphere IAU, standard parallel 0

- Crop used: data/raw/cropped_dtm.tif, 4000 x 4000 px, projected x 4587600 to 4591600 m, y 1092600 to 1096600 m (about 3.8 km east-west and 4 km north-south on the ground)

- License: CC0 1.0 Universal (USGS data release page, checked 2026-11-14). The USGS product page also asks users to cite the authors.

- Known issues: stereo DTM artifacts and seams
- Slope limitation: Slope was computed with numpy gradient using 1 m spacing in both directions (taken from the raster transform). In this equirectangular projection (standard parallel 0) one east-west pixel is about 0.95 m on the ground at latitude 18.5 deg, so the east-west gradient component, and therefore the slope, is underestimated by up to about 5 percent. Not corrected, to keep the inputs of the routing validation fixed; Austin reports this as a limitation.
