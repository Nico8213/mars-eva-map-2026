# VN research cards: Perseverance traverse data (for route validation)

Notes for readers:
- Two kinds of sources: (1) NASA MMGIS files M20_traverse.json and M20_waypoints.json, which the team snapshot uses; (2) the PDS "Mars 2020 Rover PLACES Bundle", the authoritative archived source.
- I could NOT download any data file in the AI session, so file sizes, row counts and SHA-256 values are not in this file. Whoever holds the 2026-10-11 snapshot must add them.
- Accessed on 2026-11-14 for all cards.

# Research card: Team validation files M20_traverse.json and M20_waypoints.json
- Finding: The team validation uses two files from NASA's Mars 2020 map server (MMGIS): M20_traverse.json (the driven path, as line segments) and M20_waypoints.json (points, one per drive end, with a "sol" attribute). Addresses: https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_traverse.json and https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json. These addresses are NOT linked in the text of NASA's official location-map page, and I found no NASA document describing the files. They appear in several independent open-source projects (a movingpandas example, mars-base-planner, marswalk-planner and others). One project README describes the waypoints file as NASA's live, hourly-updated feed and says the server sends no CORS headers, so a web page cannot fetch it from another site (download a copy instead). Because the files are live, a "version" can only be: download date + last sol + SHA-256. Team record (PRD v0.3 section 7.4): snapshot of 2026-10-11, last sol 1980, 703 points, 556 line segments (team script; not checked by a second person). I did not open or download the files.
- Source URL: https://movingpandas.github.io/movingpandas-website/2-analysis-examples/mars-rover.html ; https://github.com/YuXuan-Ding/mars-base-planner ; https://github.com/enomis-dev/perseverance-traverse-3d ; https://github.com/ammarzulfaqar/marswalk-planner
- Organization / author: NASA/JPL-Caltech (files, per third-party descriptions); third-party projects (evidence of the addresses)
- Version / date: no version number (live files); team snapshot 2026-10-11, sol 1980
- Accessed on: 2026-11-14 (pages above; the files themselves were not opened)
- License: see the license card below
- Confidence: medium (addresses confirmed by several third-party projects; NASA documentation not found; files not opened)

# Research card: NASA official location-map page check
- Finding: The NASA page "Where is Perseverance?" (last updated 13 Oct 2026) embeds an interactive map (https://mars.nasa.gov/map/) of the rover's latest location and traverse path. It says the map has two layers (a high-resolution color HiRISE map of the initial exploration area inside Jezero, and a Northeast Syrtis regional color map from the ESA Mars Express HRSC camera), that a high-resolution DEM was made for rover drivers, and that each dot is the end point of a drive labeled with the sol on which the rover stopped. The page text I read has no link to M20_traverse.json or M20_waypoints.json, no download link and no license statement. It also reports that on 11 Oct 2026 the odometer reached 45.22 km (28.10 miles).
- Source URL: https://science.nasa.gov/mission/mars-2020-perseverance/location-map/
- Organization / author: NASA Science (page editor listed: Stephen Carney)
- Version / date: page last updated 2026-10-13
- Accessed on: 2026-11-14
- License: Not stated on the page
- Confidence: high for what the page says; the interactive map itself may contain links I could not see in the page text

# Research card: Use statement for the NASA JSON files
- Finding: No license or use statement was found on the official page or for the files themselves. NASA's general Images and Media Usage Guidelines say NASA content (images, audio, video and media files) is generally not subject to copyright in the United States for non-commercial use; these guidelines are written for media, not specifically for data files, and logos and identifiers are not public domain. A third-party README (marswalk-planner) calls the traverse file "public domain", but that is not a NASA statement. Suggested wording for the citation table: "NASA/JPL-Caltech, Mars 2020 MMGIS traverse and waypoints, downloaded <date>, license: not stated; NASA media usage guidelines apply (generally not copyrighted, non-commercial use)". Nico should confirm this against the Space Apps rules.
- Source URL: https://www.nasa.gov/nasa-brand-center/images-and-media/ ; https://www.jpl.nasa.gov/jpl-image-use-policy/
- Organization / author: NASA; JPL
- Version / date: NASA guidelines page updated 2026-08-13
- Accessed on: 2026-11-14
- License: Not stated for the files; NASA media guidelines as above
- Confidence: medium

# Research card: Authoritative archive - Mars 2020 Rover PLACES Bundle (PDS)
- Finding: The PDS Geosciences Node archives the rover's localized positions in the "Mars 2020 Rover PLACES Bundle" (PLACES = Position Localization and Attitude Correction Estimate Storage). Release 16 was posted on 11 Aug 2026 and, per the page, covers 2021-02-18 through 2026-06-21, or sols 0 to 1897. The PRD cites Release 15 (sols 0-1762), so the citation should name the release actually used. Each release is a complete bundle with six collections (data_localizations, data_mechanisms, data_maps, data_orbital, data_ancillary, document).
- Source URL: https://pds-geosciences.wustl.edu/missions/mars2020/places.htm ; https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/
- Organization / author: NASA PDS Geosciences Node; data prepared by the Mars 2020 project (JPL)
- Version / date: Release 16, 2026-08-11 (data through 2026-06-21, sols 0-1897)
- Accessed on: 2026-11-14
- License: Not stated on the page; PDS general statements are in vn-crism.md (PDS FAQ: PDS data sets are in the public domain)
- Confidence: high

# Research card: PLACES - which files, and the three views
- Finding: Most users need three files: best_interp.csv (data_localizations), m20_orbital_map.img and m20_orbital_dem.img (data_maps; use the .img files and their labels, not the PNG browse images). Three views exist: telemetry (positions reported by the rover, not corrected, drift from wheel slip); best_tactical (corrected by the Mars 2020 Localization team using Navcam images and HiRISE, expected accuracy 0.5 m compared to the base map, sparse, typically the last drive of each sol); best_interp (all best_tactical points plus interpolated points in between, a continuous path, assuming errors are spread evenly along each drive). Interpolated points are approximations.
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/Mars2020_Rover_PLACES_PDS_SIS.pdf
- Organization / author: Deen, R. (JPL), "Rover PLACES Data Products for PDS", Software Interface Specification
- Version / date: SIS v1.0, 2022-02-22
- Accessed on: 2026-11-14
- License: Copyright California Institute of Technology, government sponsorship acknowledged (as printed in the SIS)
- Confidence: high

# Research card: PLACES - file format and coordinate system
- Finding: best_interp.csv is a CSV with 28 columns, including frame, site, drive, pose, northing, easting, planetocentric_latitude, planetodetic_latitude, longitude (east positive), elevation (up positive, referenced to the MOLA areoid), map_pixel_line/sample, dem_pixel_line/sample, roll, pitch, yaw, quaternion, sclk and sol; -9999 means not available. PLACES Z is positive down (opposite to elevation); X is northing and Y is easting. Map projection: equirectangular, standard parallel 18.4663 degrees, origin at Airy-0, Mars ellipsoid radius 3,396,190 m used by the rover team; easting meters are measured at the standard parallel, northing meters are true meters. The pixel columns tell exactly where the point falls on the map and DEM.
- Source URL: same SIS as above
- Organization / author: Deen, R. (JPL)
- Version / date: SIS v1.0, 2022-02-22
- Accessed on: 2026-11-14
- License: see the SIS card
- Confidence: high for the conventions (copied from the SIS); the real file has not been opened

# Research card: PLACES - base map and elevation model
- Finding: The base map is a 52,000 x 36,000 pixel mosaic at 0.25 m/pixel made mainly from USGS-processed HiRISE orthophotos with CTX fill, registered to the Mars Express HRSC 50 m DEM and then to MOLA. The matching DEM is 1.0 m/pixel from USGS HiRISE DEMs. Each PLACES release contains only cutouts covering the rover path plus about 500 m on all sides. The SIS shows how to convert with GDAL: gdal_translate m20_orbital_map.img m20_orbital_map.tif.
- Source URL: SIS above ; https://astrogeology.usgs.gov/search/map/Mars/Mars2020/JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first
- Organization / author: Deen, R. (JPL); Mars 2020 Localization Team with USGS
- Version / date: SIS v1.0, 2022-02-22; USGS page not opened by me
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: high for the description; unknown: file sizes in MB and the USGS map license

# Research card: Cautions for using the path in route validation
- Finding: (1) Release notes: since release 4 the ROVER,n,0 rows were removed from best_interp.csv and best_tactical.csv; use the SITE,n row for those positions and take orientation from telemetry.csv. (2) Roll, pitch and yaw are copied from telemetry, not adjusted. (3) The path is an estimate, not ground truth. (4) PLACES is organized by rover motion counter (site/drive), not by sol. (5) The page says Release 16 starts on 2021-02-18 but the release notes text says 2022-02-18 (both say sols 0-1897); the first date in the release notes is probably a typo (the rover landed on 18 Feb 2021), not confirmed by PDS. (6) PLACES covers only to sol 1897, while the team snapshot goes to sol 1980; if PLACES is used as the reference, the validation segment must lie at or below sol 1897. (7) Use the same DEM for the slope map and the path.
- Source URL: https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/release_notes.txt ; PLACES page and SIS above ; PRD v0.3 section 7.4
- Organization / author: NASA PDS Geosciences Node; Deen, R. (JPL)
- Version / date: release notes updated with Release 16
- Accessed on: 2026-11-14
- License: see the first PLACES card
- Confidence: high for items 1-4; item 5 is my reading; items 6-7 are our advice

# Research card: Check values from the PLACES SIS example (landing site)
- Finding: The SIS example best_interp.csv first row (SITE,1, the landing site): planetocentric latitude 18.444627146, planetodetic latitude 18.346169209, longitude 77.450885729, elevation -2569.910 m. Use only as a sanity check on the real file's first row (not live data).
- Source URL: SIS above
- Organization / author: Deen, R. (JPL)
- Version / date: SIS v1.0, 2022-02-22
- Accessed on: 2026-11-14
- License: see the SIS card
- Confidence: medium

# Research card: Backup - PDS Analyst's Notebook (shapefile and Excel export)
- Finding: The Mars 2020 Analyst's Notebook (https://an.rsl.wustl.edu/m20/) shows waypoints and the drive traverse built from interpolated PLACES locations over a HiRISE basemap. Conference abstracts (2023, 2024) say traverse data and maps can be downloaded from its Resources tab or the Traverse map settings and exported as Excel and Shapefile. I did not open the tool.
- Source URL: https://pds-geosciences.wustl.edu/workshops/LPSC2024/1255.pdf ; https://pds-geosciences.wustl.edu/workshops/LPSC2023/2194.pdf
- Organization / author: Stein, T. C., Arvidson, R. E., Zhou, F., et al. (PDS Geosciences Node)
- Version / date: LPSC 2023 and 2024 abstracts
- Accessed on: 2026-11-14
- License: Not found on the pages I checked
- Confidence: medium

Still to check:
- Who holds the 2026-10-11 snapshot files, their SHA-256 and where they are stored (PRD section 7.4 gives only counts: 703 points, 556 segments, sol 1980)
- Whether NASA documents these two JSON files anywhere (field names, coordinate system, accuracy)
- Download PLACES best_interp.csv, m20_orbital_map.img and m20_orbital_dem.img and record sizes and row counts
- Confirm the Release 16 date range with PDS (2021 vs 2022 in the release notes) and the PLACES DOI (https://pds-geosciences.wustl.edu/dataserv/doi.htm)
- Check that Xin En's DEM and the PLACES map use the same projection (standard parallel 18.4663 degrees)
