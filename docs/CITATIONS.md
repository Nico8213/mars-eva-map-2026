# Citations

<!-- Team note, delete before final submission: every row in the first table must have no TBD left. Move or delete unused rows. Search this file for "TBD" and "PRD" before submitting. -->

Every source used in this project is listed here, including open and freely available ones. Columns: Name, Organization, Version, URL, Accessed, License, Used in.

## 1. Data and software used

| Name | Organization | Version | URL | Accessed | License | Used in |
| --- | --- | --- | --- | --- | --- | --- |
| HiRISE DTM (Jezero crop) | USGS Astrogeology Science Center | TBD (exact version as downloaded, see data/processed/sources.md), 1 m/px | https://doi.org/10.5066/P9REJ9JN | 2026-11-14 (downloaded) | TBD | Terrain layer (F1); slope raster for route cost (F3) |
| CTX orthorectified mosaic | TBD | TBD, 5 m/px | TBD | TBD | TBD | Optical layer (F1) |
| HiRISE orthorectified image | TBD | TBD, 0.25 m/px | TBD | TBD | TBD | Optical layer (F1) |
| CRISM data archived at the PDS | NASA PDS Geosciences Node; MRO CRISM team | TBD (product ID or DOI of the product behind the layer; the PDS lists MRDR v4 and MTRDR/TER Release 19) | https://pds-geosciences.wustl.edu/missions/mro/crism.htm | 2026-11-14 | No access or use restrictions stated by PDS; cite as published research. Statement: https://pds-geosciences.wustl.edu/faq.html | POI source (F2); route endpoint selection (F3) |
| JMARS (viewer) and its CRISM hydrous mineral detections layer | TBD (JMARS team) | TBD | TBD | TBD | TBD (JMARS terms not yet checked) | Screenshot used to place points of interest by hand |
| Perseverance traverse and waypoints (M20_traverse.json, M20_waypoints.json) | NASA/JPL-Caltech (Mars 2020 "Where is Perseverance?" map). Cross-reference: PLACES Release 15 (sols 0-1762) | Snapshot 2026-10-11, last sol 1980 | https://science.nasa.gov/mission/mars-2020-perseverance/location-map/ ; JSON files: https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_traverse.json and https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json (addresses to be confirmed against the official page) | 2026-10-11 (to confirm against file timestamp) | TBD | Validation reference only (F7) |
| MEDA Radiation and Dust Sensor (RDS) data | NASA PDS Atmospheres Node (Rodriguez-Manfredi et al., 2021) | DOI 10.17189/1522849 (MEDA bundle); data from 19 Feb 2021, ongoing | https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/PERSEVERANCE/meda.html | 2026-11-14 | TBD | Environment reference panel (F9). RDS uses UV photodiodes: it measures sunlight (UV), not radiation dose |
| MEDA derived dataset (TIRS, PS, RHS) | NASA PDS Atmospheres Node | DOI 10.17189/1522849 (MEDA bundle); coverage sol 1-1859 (to verify) | https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/PERSEVERANCE/meda.html | TBD | TBD | Atmospheric background, one sentence only |
| Mastcam-Z aerosol optical depth dataset, Jezero | Lemmon, M., Space Science Institute (Boulder, CO), Mendeley Data | Version 2, published 7 Apr 2026, DOI 10.17632/gktjp9jptb.2 | https://data.mendeley.com/datasets/gktjp9jptb/2 | 2026-11-14 | CC BY 4.0 (confirmed on the dataset page) | Environment reference panel, dust (F9) |
| Curiosity RAD dose data, Gale crater (not Jezero) | Hassler, D. M., Zeitlin, C., et al. (Southwest Research Institute), Science | Science 343(6169), 2014, DOI 10.1126/science.1244797 | https://ntrs.nasa.gov/citations/20180007641 | 2026-11-14 | TBD | Analogy reference only; not a Jezero value |
| Leaflet | Volodymyr Agafonkin, CloudMade (per LICENSE) | 1.9.4+v1.d15112c (per leaflet.js header) | https://leafletjs.com/ | TBD | BSD 2-Clause (LICENSE file kept in web/vendor/leaflet/) | Web map (web/vendor/leaflet) |
| Python packages listed in the requirements files | Various open-source authors | As pinned in requirements files | https://pypi.org/ | TBD | TBD (list each package and its license) | data pipeline, routing, validation |

## 2. Candidate sources (delete a row if it is not used in the submission)

| Name | Organization | Version | URL | Accessed | License | Used in |
| --- | --- | --- | --- | --- | --- | --- |
| MOLA-HRSC blended DEM | TBD | TBD, 200 m/px | TBD | TBD | TBD | Regional background only; not used for slope |
| MRO MCS DDR V6.2 | TBD | V6.2 | TBD | TBD | TBD | Environment reference candidate; Jezero coverage and license unchecked |

## 3. Literature cited

| Reference | Used in |
| --- | --- |
| Seelos, F. P., et al. (2023). The CRISM investigation in Mars orbit: Overview, history, and delivered data products. Icarus. https://authors.library.caltech.edu/records/h6pv6-fhf02 | Background on CRISM data |
| Brown, A. J., Viviano, C. E., Goudge, T. A. (2020). Olivine-carbonate mineralogy of the Jezero crater region. Journal of Geophysical Research: Planets. https://doi.org/10.1029/2019JE006011 | Background on CRISM coverage of Jezero |
| Minetti, A. E., et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. https://iris.unibs.it/handle/11379/540545 | Cost function (routing spec, section 2) |
