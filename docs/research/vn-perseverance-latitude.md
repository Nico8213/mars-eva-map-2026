VN research card: latitude type and datum of Perseverance position data

Prepared for: docs/research/vn-perseverance-latitude.md Date viewed: 2026-11-15 (all links opened on this date; re-open and confirm before final submission) Confidence labels used: "Stated in official documentation" / "Indirect inference" / "Not found"

Part 1. PLACES best_interp.csv, column planetocentric_latitude

Data checked: Mars 2020 Rover PLACES bundle, file best_interp.csv in the data_localizations collection Official document: Rover PLACES Data Products for PDS, Software Interface Specification (SIS), Version 1.0, 2022-02-22, prepared by Robert Deen, JPL Source link (SIS): https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/Mars2020_Rover_PLACES_PDS_SIS.pdf Source link (bundle page): https://pds-geosciences.wustl.edu/missions/mars2020/places.htm

Finding 1: Latitude type Conclusion: planetocentric_latitude is planetocentric latitude (angle measured from the center of the planet). The SIS also provides a separate column, planetodetic_latitude. Source: SIS Section 5.1.3 (Per-View CSV File), field definitions Confidence: Stated in official documentation

Finding 2: Reference surface for planetocentric_latitude Conclusion: The SIS computes planetocentric_latitude from the PLACES northing with one radius, Re = 3396190 m, using latitude = (northing / Re) x (180 / pi). The SIS calls Re the "ellipsoid radius". Because the formula uses a single radius, and the SIS says the map label sets all three axis radii (A, B, C) to the same value (the Mars spherical radius), the reference is a sphere of radius 3396190 m. Source: SIS Section 5.1.3 (formula) and Section 5.2.3 (map label keywords A_AXIS_RADIUS, B_AXIS_RADIUS, C_AXIS_RADIUS) Confidence: Stated in official documentation (formula and radius). The wording "sphere" follows the SIS statement that all three axis radii are the same. Note: In Section 5.2.3 the SIS text writes the radius as 3393190 m, but the label example in the same section and every formula use 3396190 m (3396.19 km). Treat 3393190 as a typo in the SIS text; do not copy it.

Finding 3: Planetodetic column (for reference only) Conclusion: The SIS defines planetodetic_latitude using Re = 3396190 m and a second radius of 3376200 m. The SIS example row shows planetocentric 18.444627146 and planetodetic 18.346169209 at the same point, a difference of about 0.1 degree at Jezero. The project should state which column it uses. Source: SIS Section 5.1.3 Confidence: Stated in official documentation. The text extraction of the planetodetic formula was garbled, so the formula itself was not verified here; do not use that column unless the formula is checked in the original PDF.

Finding 4: Longitude and easting Conclusion: Longitude is computed from easting using Re = 3396190 m and a standard parallel of 18.4663 degrees; easting is measured at that standard parallel. Mars 2020 maps use an equirectangular projection with that standard parallel. Source: SIS Sections 3.9.1, 3.9.2 and 5.1.3 Confidence: Stated in official documentation

Finding 5: Elevation datum Conclusion: Elevation in the CSV is relative to the MOLA areoid. At the landing site the areoid is 3394507.076 m from the planet center, about 1683 m below the 3396190 m reference. Source: SIS Section 3.9.3 Confidence: Stated in official documentation

Finding 6: Release number
Conclusion: The PDS bundle page states "Mars 2020 Release 16 covers all PLACES data from 2021-02-18 through 2026-06-21, or sols 0 to 1897." The release notes list Release 16 with release date 2026-08-11. (The page text gives the start date as 2021-02-18; the release notes give 2022-02-18. Not resolved.) The release notes also state that ROVER,n,0 rows are absent from best_interp.csv and best_tactical.csv; use the SITE,n row for position.
Source link: https://pds-geosciences.wustl.edu/missions/mars2020/places.htm and https://pds-geosciences.wustl.edu/m2020/urn-nasa-pds-mars2020_rover_places/document/release_notes.txt
Confidence: Stated in official documentation
Unresolved: Whether the SIS changed after Version 1.0 (2022-02-22).

Part 2. MMGIS M20_traverse.json and M20_waypoints.json

Files: https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_traverse.json and https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json

Finding 7: Latitude type of the coordinates inside the two JSON files Conclusion: Not found. No NASA/JPL documentation was found that states whether the latitude values in these two files are planetocentric or planetographic (planetodetic), or which datum they use. What was searched: the NASA MMGIS documentation site (nasa-ammos.github.io/MMGIS), the MMGIS GitHub page, and NASA's M20 location-map configuration. Confidence: Not found

Finding 8: Planetary radius configured for the NASA M20 map (not the same as the JSON latitude type) Conclusion: NASA's configuration for the Mars 2020 MMGIS map (mission "M20") sets the planetary radius with major = 3396190 and minor = 3396190, and has no custom projection set. This describes the map configuration; it does not say how the latitude values in the two JSON files were computed. Source link: https://mars.nasa.gov/maps/location/api/configure/get?mission=M20 Confidence: Stated in official configuration data (map radius only). The JSON latitude type is still Not found.

Unresolved: Ask the MMGIS contacts listed on the NASA-AMMOS MMGIS GitHub page, or the Mars 2020 location map team, which latitude type and datum the two JSON files use. Until answered, project text must say "latitude type of the MMGIS JSON files not documented" and must not label them planetocentric or planetographic. Unofficial forum and blog posts about these files were seen and are not used here.
