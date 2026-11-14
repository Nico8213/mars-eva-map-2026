# VN research cards: Perseverance traverse data (for route validation)

Notes for readers:
- Main source: NASA PDS "Mars 2020 Rover PLACES Bundle" (official, localized rover positions). Backups are listed at the end.
- Everything below was read from the PDS pages and the PLACES Software Interface Specification (SIS). I could NOT download the data files in this session, so file sizes and row counts are unknown.
- Accessed on 2026-11-14 for all cards.

# Research card: Official traverse data set - Mars 2020 Rover PLACES Bundle
- Finding: The PDS Geosciences Node (Washington University in St. Louis) archives the Perseverance rover's localizations (position and orientation along its path) in the "Mars 2020 Rover PLACES Bundle". PLACES stands for Position Localization and Attitude Correction Estimate Storage, the database used in rover operations. Release 16 was posted on 11 Aug 2026 and, per the page, covers all PLACES data from 2021-02-18 through 2026-06-21, or sols 0 to 1897. Each release is a complete bundle, so only the latest release is needed. The bundle contains six collections: data_localizations, data_mechanisms, data_maps, data_orbital, data_ancillary and document.
- Source URL: https://pds-geosciences.wustl.edu/missions/mars2020/places.htm ; bundle root: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/ ; localizations: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/data_localizations/
- Organization / author: NASA PDS Geosciences Node; data prepared by the Mars 2020 project (JPL)
- Version / date: Release 16, 2026-08-11 (data through 2026-06-21, sols 0-1897)
- Accessed on: 2026-11-14
- License: Not stated on the page; general PDS statements are in vn-crism.md; the page footer links the JPL image use policy (https://www.jpl.nasa.gov/jpl-image-use-policy)
- Confidence: high

# Research card: Which files to download
- Finding: The SIS says most users need just three files: (1) best_interp.csv in the data_localizations collection, which has the rover location and orientation at each point along the traverse; (2) m20_orbital_map.img (base map cutout) and (3) m20_orbital_dem.img (elevation cutout), both in the data_maps collection. PNG versions of the map and DEM are in browse_maps, but they carry no mapping information, so use the .img files and their labels (.xml). Values are "localized", meaning adjusted so rover images match the orbital map, which compensates for wheel slip.
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/Mars2020_Rover_PLACES_PDS_SIS.pdf
- Organization / author: Deen, R. (JPL), "Rover PLACES Data Products for PDS", Software Interface Specification
- Version / date: SIS Version 1.0, 2022-02-22 (written for the first releases; the release notes keep it current)
- Accessed on: 2026-11-14
- License: Copyright California Institute of Technology, government sponsorship acknowledged (as printed in the SIS)
- Confidence: high

# Research card: The three views (which path to use for validation)
- Finding: best_interp.csv holds the "best_interp" view. Three views exist: (a) telemetry = positions reported by the rover, not corrected on the ground, so they drift because of wheel slip and should generally not be used directly; (b) best_tactical = positions corrected by the Mars 2020 Localization team by comparing rover Navcam images with HiRISE, with an expected accuracy of 0.5 m compared to the base map, but sparse (typically the last drive of each sol); (c) best_interp = all best_tactical points plus interpolated points for the drives in between, giving a continuous path. The interpolation is an approximation that assumes errors are spread evenly along each drive.
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/Mars2020_Rover_PLACES_PDS_SIS.pdf
- Organization / author: Deen, R. (JPL)
- Version / date: SIS v1.0, 2022-02-22
- Accessed on: 2026-11-14
- License: see the first card
- Confidence: high; the 0.5 m figure is "expected accuracy at the localized points", not for interpolated points

# Research card: File format and coordinate system
- Finding: best_interp.csv is a plain CSV with 28 columns and a header line. Columns include frame (SITE or ROVER), site, drive, pose, landing_x/y/z, northing, easting, planetocentric_latitude, planetodetic_latitude, longitude, elevation, map_pixel_line, map_pixel_sample, dem_pixel_line, dem_pixel_sample, roll, pitch, yaw, four quaternion values, areoid, radius, sclk and sol. The value -9999 means "not available". Latitude is given in two types (planetocentric and planetodetic, in degrees); longitude is east-positive in degrees. Elevation is positive up and referenced to the MOLA areoid; the Z values used in PLACES are the opposite sign (positive down). In PLACES, X is northing and Y is easting. The map projection is equirectangular with a standard parallel of 18.4663 degrees, origin at Airy-0, and the rover team uses a Mars ellipsoid radius of 3,396,190 m. Easting meters are measured at the standard parallel, so they are not true meters away from it; northing meters are true meters. The SIS says the difference is not significant in the rover operations area. The SIS also gives pixel coordinates in the map and DEM, which remove any doubt about how latitude and longitude are placed on the map.
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/Mars2020_Rover_PLACES_PDS_SIS.pdf
- Organization / author: Deen, R. (JPL)
- Version / date: SIS v1.0, 2022-02-22
- Accessed on: 2026-11-14
- License: see the first card
- Confidence: high for the column list and conventions (copied from the SIS); the real file has not been opened

# Research card: Base map and elevation model that go with the path
- Finding: The base map used for all Mars 2020 localizations is a mosaic of 52,000 lines by 36,000 samples at 0.25 m/pixel covering the landing site, the Jezero delta and surrounding areas. It was made mostly from USGS-processed MRO HiRISE orthophotos, with gaps filled by MRO CTX images, and registered to the Mars Express HRSC 50 m/pixel DEM, which is registered to the MOLA DEM. The matching DEM is 1.0 m/pixel (made from USGS HiRISE DEMs, backfilled with a CTX DEM). The files in each PLACES release are cutouts covering the minimum and maximum extent of the rover path in that release plus about 500 m on all sides, not the full map. Full map metadata is on the USGS Astrogeology site. The SIS shows how to convert the .img files to GeoTIFF with GDAL: gdal_translate m20_orbital_map.img m20_orbital_map.tif (same for the DEM).
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/Mars2020_Rover_PLACES_PDS_SIS.pdf ; https://astrogeology.usgs.gov/search/map/Mars/Mars2020/JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first
- Organization / author: Deen, R. (JPL); Mars 2020 Localization Team with USGS (map)
- Version / date: SIS v1.0, 2022-02-22; USGS page not opened by me, only its link from the SIS
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: high for the description; unknown: size in MB of the delivered files, and the license of the USGS map

# Research card: Cautions for using the path in route validation
- Finding: (1) The release notes say that since release 4 the ROVER,n,0 rows were removed from best_interp.csv and best_tactical.csv because of technical difficulties; for those points use the SITE,n row for the position, and take orientation from telemetry.csv (highest pose). (2) Orientation (roll, pitch, yaw) in best_tactical and best_interp is copied from telemetry because the localization team does not adjust it. (3) The path is a localized and interpolated estimate, not ground truth; the SIS says the true position is unknowable and every solution is an estimate. (4) PLACES is organized by rover motion counter (site/drive), not by sol, so each release contains more than its nominal sol range. (5) Release notes dates: the page says Release 16 covers 2021-02-18 through 2026-06-21, but the release notes text says 2022-02-18 through 2026-06-21 (both say sols 0 to 1897); the rover landed on 18 Feb 2021, so the first date in the release notes is probably a repeated typo; this was not confirmed by PDS. (6) Z in PLACES is positive down, elevation positive up; do not mix them. (7) Use the same DEM for the slope map and for the rover path, or the slopes along the path will not match.
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/release_notes.txt ; https://pds-geosciences.wustl.edu/missions/mars2020/places.htm ; SIS URL above
- Organization / author: NASA PDS Geosciences Node; Deen, R. (JPL)
- Version / date: release notes updated with Release 16 (2026-08-11)
- Accessed on: 2026-11-14
- License: see the first card
- Confidence: high for items 1-4 and 6; item 5 is my reading of a discrepancy; item 7 is advice from us, not from the source

# Research card: Check values from the SIS example (landing site)
- Finding: The SIS shows an example best_interp.csv with the first row for the landing site (SITE,1): planetocentric latitude 18.444627146, planetodetic latitude 18.346169209, longitude 77.450885729, elevation -2569.910 m, areoid 3394507.076 m. Use this only as a sanity check when the real file is opened (the first row should be close to these values). These come from the example in the document, not from the live release.
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/Mars2020_Rover_PLACES_PDS_SIS.pdf
- Organization / author: Deen, R. (JPL)
- Version / date: SIS v1.0, 2022-02-22
- Accessed on: 2026-11-14
- License: see the first card
- Confidence: medium (document example, not live data)

# Research card: Backup 1 - PDS Analyst's Notebook (map with shapefile and Excel downloads)
- Finding: The PDS Geosciences Node also runs the Mars 2020 Analyst's Notebook (https://an.rsl.wustl.edu/m20/), a web tool that shows Perseverance data by sol and location. Its map shows rover waypoints and the drive traverse, built from interpolated locations from the PLACES archive, over a HiRISE basemap. A 2024 conference abstract says rover drive telemetry data and maps can be downloaded from a link in the Resources tab or from the Traverse map settings panel, and that measurements and map content can be exported as Excel spreadsheets and Shapefiles (Z values included in Shapefile exports since 2023). I have not opened the tool, so the current download steps may differ.
- Source URL: https://pds-geosciences.wustl.edu/workshops/LPSC2024/1255.pdf ; https://pds-geosciences.wustl.edu/workshops/LPSC2023/2194.pdf ; https://pds-geosciences.wustl.edu/workshops/LPSC2023/2166.pdf
- Organization / author: Stein, T. C., Arvidson, R. E., Zhou, F., Hughes, M. et al. (PDS Geosciences Node, Washington University in St. Louis)
- Version / date: LPSC 2023 and LPSC 2024 abstracts
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: medium (conference abstracts; tool not tested)

# Research card: Backup 2 - NASA "Where is Perseverance?" map (waypoints file, unofficial URL)
- Finding: NASA's interactive map shows the path Perseverance took and its location at the end of every sol (https://science.nasa.gov/mission/mars-2020-perseverance/location-map/). A 2025 blog post (R-bloggers) reads a GeoJSON file from https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json and plots it by sol, so a waypoints file with a "sol" attribute exists at that address. A Wikipedia user page also says waypoints can be exported as GeoJSON from the NASA map. I found no NASA documentation describing this file's coordinate system, accuracy or license, so treat it only as a quick visual check, not as the validation reference.
- Source URL: https://www.r-bloggers.com/2025/11/perseverance/ ; https://science.nasa.gov/mission/mars-2020-perseverance/location-map/
- Organization / author: NASA (map); R-bloggers post (third party)
- Version / date: blog 2025-11
- Accessed on: 2026-11-14
- License: Not found
- Confidence: low to medium (the file address comes from a third party; I did not open it)

# Research card: Backup 3 - Geologic context shapefiles along the early traverse
- Finding: A Mendeley Data set from L. Crumpler contains GIS shapefiles of an in situ geologic mapping transect on the floor of Jezero crater, built from Perseverance observations. It was published on 2 Nov 2022 (Version 1, DOI 10.17632/7jf5jdwh3g.1). The related paper (Crumpler et al., JGR Planets, 2023) describes a nearly continuous geologic record over a 120 m wide corridor along the rover traverse. It covers only the early floor traverse, so it is not a full path data set. The "Licence" field was blank in the page text I saw.
- Source URL: https://data.mendeley.com/datasets/7jf5jdwh3g/1 ; https://ntrs.nasa.gov/api/citations/20230016438/downloads/Crumpler%20et%20al%202023%20JGR%20Planets%20Mapping%20of%20Jezero.pdf
- Organization / author: Crumpler, L. S., Horgan, B. H. N., Simon, J. I., Stack, K. M., et al.
- Version / date: data set v1, 2022-11-02; paper 2023
- Accessed on: 2026-11-14
- License: Not shown in the text I saw (check the Mendeley page)
- Confidence: medium

Still to check:
- Download best_interp.csv, m20_orbital_map.img and m20_orbital_dem.img from the latest release and record their file sizes and row counts (PDS pages did not list sizes; the Mars 2020 bundle may be large, so download only the three files above)
- Confirm the Release 16 date range with PDS (2021-02-18 vs 2022-02-18 start date in the release notes)
- The PLACES bundle DOI (see https://pds-geosciences.wustl.edu/dataserv/doi.htm) and the exact citation text to use in docs/CITATIONS.md
- A license or use statement for PDS Geosciences data and for the USGS Mars 2020 base map
- Check that the DEM Xin En uses for slope is in the same projection as the PLACES map and DEM (equirectangular, standard parallel 18.4663 degrees), or convert the path
- Whether the traverse after the crater floor (delta, crater rim) is within the cutout extent that Xin En crops for Jezero
