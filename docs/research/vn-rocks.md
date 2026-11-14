# VN research cards: Jezero rock and mineral data (for the F5 decision)

Notes for readers:
- Question: is there open rock or mineral data for Jezero, where is it, and what are its limits?
- Short answer: yes, several data sets exist, but none is a ready-made, complete mineral map of Jezero. The easiest usable layer is the USGS geologic unit map (vector). Mineral abundance maps exist only for a few CRISM image footprints.
- I could not download any file in this session, so sizes are copied from the web pages only.
- Accessed on 2026-11-14 for all cards.

# Research card: USGS geologic map of Jezero crater and the Nili Planum region (best candidate for a rock/unit layer)
- Finding: USGS Scientific Investigations Map 3464 is a continuous geologic map of Jezero crater and the Nili Planum region at 1:75,000 scale. It covers an area of about 1 degree by 1 degree (about 60 by 60 km) and is based on a 6 m/pixel CTX mosaic, with THEMIS night IR, CTX and HRSC elevation data and HiRISE images used to help identify units. Units are defined by texture, tone, morphology, margins, location and stratigraphic relations (what is visible in the images), not by direct composition measurements. A GIS version exists: "Database (349.3 MB zip)", with a Read Me; the full map PDF is 36.4 MB. The map is also published as an interactive web map. The USGS Read Me says the GIS database uses a transverse Mercator projection (rasters in MTM) and a semi-controlled CTX mosaic made before the controlled CTX mosaic released in July 2020, so alignment with later maps may be slightly off.
- Source URL: https://pubs.usgs.gov/publication/sim3464 ; https://pubs.usgs.gov/sim/3464/sim3464_readme.txt
- Organization / author: Sun, V. Z., and Stack, K. M., U.S. Geological Survey, Scientific Investigations Map 3464 (2020), DOI 10.3133/sim3464
- Version / date: 2020 (pamphlet 14 p., 1 sheet, scale 1:75,000)
- Accessed on: 2026-11-14
- License: A USGS page for the map file says "Public Domain" (https://www.usgs.gov/index.php/media/files/geologic-map-jezero-crater-and-nili-planum-region); a separate license for the GIS database was not stated. The Read Me asks users to cite the original publication.
- Confidence: high for what it is and its size; unknown: exact map bounds (the abstract text I saw was garbled; a library record gives about E 77.0-77.8 degrees and N 17.8-18.6 degrees) and the list of unit names

# Research card: Caution - the 2020 unit map was made before landing
- Finding: The USGS map was published before Perseverance landed. A USGS/JPL news release says it proposed hypotheses to be tested by the rover, for example that the Jezero crater floor might be an airfall deposit rather than a volcanic unit. Perseverance later found that the crater floor consists of igneous rocks altered by water (Seitah and Maaz units; see vn-geology.md). So unit descriptions and interpretations from the 2020 map may now be outdated; the unit outlines and names are still useful as a base, but any rock-type labels on our website must say they are pre-landing orbital interpretations.
- Source URL: https://www.usgs.gov/index.php/news/usgs-and-jpl-release-new-geologic-map-mars-2020-perseverance-rover-landing-site ; https://researchconnect.stonybrook.edu/en/publications/aqueously-altered-igneous-rocks-sampled-on-the-floor-of-jezero-cr/
- Organization / author: USGS and JPL (news release, 2020-12-11); Farley, K. A. et al., Science 377(6614), eabo2196 (2022)
- Version / date: 2020-12-11; 2022-09-30
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: high

# Research card: CRISM carbonate and olivine abundance maps for Jezero (Zenodo)
- Finding: A public Zenodo data set accompanies the paper "Distinct Carbonate Lithologies in Jezero Crater, Mars" (Zastrow and Glotch, GRL 48, 2021). The authors ran spectral mixture analysis on three CRISM visible/near-infrared images over Jezero, modeled carbonate abundances up to about 35% per pixel, identified three distinct carbonate-bearing units, and found that olivine is mostly in sand deposits lying on carbonate-bearing rocks. Files: code_unmixing.zip (49.1 kB), data_input.zip (1.4 GB, ENVI image cubes), data_models.zip (6.8 GB, NetCDF model output registered to HiRISE, with mineral concentration maps), data_roi.zip (60.7 kB, shapefile of mapped regions of interest). Total 8.1 GB, so only data_roi.zip is practical for a one-day project; the large files would need cropping first. Coverage is limited to those three CRISM footprints, not the whole crater.
- Source URL: https://zenodo.org/records/4699583
- Organization / author: Zastrow, A. M., and Glotch, T. D., Stony Brook University
- Version / date: Version 1.2.0, published 31 Dec 2020, DOI 10.5281/zenodo.4699583
- Accessed on: 2026-11-14
- License: Creative Commons Attribution 4.0 International (stated on the Zenodo page)
- Confidence: high for the contents and license; unknown: the actual map extents

# Research card: Published mineral-unit studies (no downloadable map found)
- Finding: Several papers map Jezero minerals from CRISM data, but I found no download link for their maps. Brown et al. (JGR Planets, 2020, DOI 10.1029/2019JE006011) use CRISM to map olivine and carbonates in the crater and watershed. Horgan et al. (Icarus, 2020, DOI 10.1016/j.icarus.2019.113526) identify a distinct carbonate-bearing unit, the "Marginal Carbonates", that may preserve lacustrine carbonates. A summary based on Brown et al. cites the olivine-carbonate unit across the wider Nili Fossae region mapped by Kremer et al. (2019). One review paper says Jezero has three main mineral units: an olivine/carbonate-rich unit, a mafic capping floor unit with no hydrated minerals detected, and the delta deposit, dominated by Fe/Mg smectites and low-calcium pyroxene with isolated Mg-carbonate and olivine. These are paper results, so they can be cited as text but not drawn as a layer without the authors' data.
- Source URL: https://arxiv.org/pdf/1904.11414 ; https://www.usgs.gov/publications/mineral-diversity-jezero-crater-evidence-possible-lacustrine-carbonates-mars ; https://arxiv.org/pdf/2110.15428 ; https://astrobiology.nasa.gov/news/serpenitinzation-and-astrobiological-potential-of-the-mars-2020-landing-site/
- Organization / author: Brown, A. J., Viviano, C. E., Goudge, T. A.; Horgan, B. H. N., Anderson, R. B., Dromart, G., Amador, E. S., Rice, M. S.; SuperCam IR instrument paper (arXiv 2110.15428); NASA Astrobiology news
- Version / date: 2020; arXiv 2021
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: medium (read from abstracts and summaries)

# Research card: Where CRISM products come from
- Finding: Orbital mineral information for Jezero starts from MRO CRISM products in the PDS Geosciences Node (details, versions and coverage limits are in vn-crism.md). A NASA caption says CRISM data (combined with the Context Camera) show that the Jezero delta sediments contain clays and carbonates. Targeted CRISM images cover small patches, so a full-crater mineral layer would need more than the targeted products.
- Source URL: https://www.nasa.gov/news-release/nasa-announces-landing-site-for-mars-2020-rover/ ; https://pds-geosciences.wustl.edu/missions/mro/crism.htm
- Organization / author: NASA; PDS Geosciences Node
- Version / date: NASA release 2018-11-19
- Accessed on: 2026-11-14
- License: see vn-crism.md
- Confidence: high for the NASA caption statement; see vn-crism.md for coverage

# Research card: Rover-measured rock chemistry (point data along the traverse)
- Finding: Perseverance's instruments produce measured chemistry of rocks, archived at the PDS Geosciences Node. PIXL (X-ray lithochemistry) bundles contain oxide and element abundances by point (PMC); the elements and oxides include Na2O, MgO, Al2O3, SiO2, P2O5, SO3, Cl, K2O, CaO, TiO2, Cr2O3, MnO, FeO-T, NiO, ZnO and Br; the data are not normalized to 100 wt%, and sodium can have large uncertainties. SuperCam bundles contain calibrated LIBS, Raman, VISIR and IR spectra and an observation log. The page I read lists PIXL Release 10 (2024) and SuperCam Release 14 (4 Dec 2025), but a PIXL readme in a folder dated 2026-08-11 also exists, so the PIXL page may be out of date. These are measurements at points the rover visited, not an area map, so they could mark sample locations but not shade a map layer.
- Source URL: https://pds-geosciences.wustl.edu/missions/mars2020/pixl.htm ; https://pds-geosciences.wustl.edu/missions/mars2020/supercam.htm ; https://pds.nasa.gov/data/pds4/releases/geo/mars2020_pixl-20260811/readme.txt
- Organization / author: NASA PDS Geosciences Node; PIXL and SuperCam teams
- Version / date: PIXL Release 10 (2024-07-30) on the page; SuperCam Release 14 (2025-12-04)
- Accessed on: 2026-11-14
- License: Not found on the pages I checked; general PDS statements are in vn-crism.md
- Confidence: medium (pages read, no files opened)

# Research card: Summary for the F5 decision
- Finding: What exists for a "rock/mineral" layer: (1) USGS geologic unit polygons for the whole Jezero area, public domain, 349.3 MB zip (best candidate, but orbital image-based, pre-landing); (2) CRISM carbonate/olivine abundance maps for only three CRISM footprints, CC BY 4.0, mostly too large for a one-day project; (3) point chemistry from the rover at its stops; (4) paper results with no downloadable maps. What does NOT exist (as far as I found): a complete, open, ready-to-use mineral abundance map of the whole crater. Suggestion for the team to decide (not a fact): either use the USGS unit polygons with a clear label that units are pre-landing orbital interpretations, or write in the docs that the project only uses slope constraints.
- Source URL: see the cards above
- Organization / author: n/a (summary by VN)
- Version / date: n/a
- Accessed on: 2026-11-14
- License: n/a
- Confidence: medium (based on what I could find in one search session)

Still to check:
- Download the USGS SIM 3464 GIS database (349.3 MB) and list the unit names, polygon layers, projection and exact extent; check whether the database has a license statement apart from the map
- Whether any data set in the PDS or USGS gives a Jezero-wide CRISM mineral map (for example summary-parameter mosaics) and its license
- Map extents of the three CRISM footprints in the Zenodo data set (FRT000047A3 is named in a source; the other two were not identified)
- Whether the unit polygons are aligned with Xin En's DEM crop (projection and coordinate system)
- Newer maps after the rover landing (for example floor and delta units from the rover campaigns) that might replace the pre-landing unit map
