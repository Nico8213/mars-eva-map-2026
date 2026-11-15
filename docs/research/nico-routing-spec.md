# Routing specification (written by Nico)

## 1. Goal
Find the lowest-cost walking route between two points of interest on the slope grid.

## 2. Cost function
- Input: `data/processed/slope.npy` (2D array, slope in degrees, same size as `grid.json`). Slope is treated as an unsigned magnitude; uphill and downhill are not distinguished.
- Cost per cell: `cost = 1 + (slope / limit)^2`, with `limit = 20` degrees. A flat cell costs 1; a cell at the limit costs 2.
- Reason and source: This is a simple heuristic chosen for transparency. It is not fitted to data. It is qualitatively consistent with Minetti et al. (2002), who measured that the energy cost of walking rises on positive slopes: https://iris.unibs.it/handle/11379/540545
- Limitation: Minetti's data were measured under Earth gravity, with treadmill slopes between -0.45 and +0.45 (gradient, i.e. rise/run). Mars gravity is lower. Results are a relative cost ranking, not a prediction of real energy use.
- Cells steeper than 20 degrees are blocked (cost = infinity, never entered).
- Reason and source for 20 degrees: The Perseverance rover's ascent of the Jezero Crater rim was the first time a Mars rover attempted slopes greater than 20 degrees with autonomous navigation: https://robotics.jpl.nasa.gov/media/documents/2026_RO_AAS_final.pdf . This is a rover reference, not a spacesuit or human limit. No suited-EVA slope limit source was found. The value is a team choice and is stored in `routing/config.json` so it can be changed.
- Cells with no data (NaN or invalid) are blocked.

## 3. Start and end points
- Rule for choosing them: from the landing site to each point of interest in `data/processed/poi.geojson`.
- If a point of interest lies on a blocked cell, or no path exists, the route is reported as "unreachable". No fallback endpoint is invented. (Validation routes follow the separate endpoint rule in 4.6.)
- Path search: `skimage.graph.route_through_array` with `fully_connected=True` and `geometric=True`.

## 4. Validation

### 4.1 Conventions and locking rules
Tags used below:
- **[SOURCE]** is a fact taken from a document or a file. The source is named.
- **[DESIGN]** is our own choice, not a measured or published number. It is fixed here, before any result exists, and must not change afterwards (project plan §9.2, §9.4).
- **[TBD-DATA]** can only be filled by opening the real file. Do not type a guess. Write the value read from the file, with the command or script that produced it.

"Project plan" means the team's internal planning document. It is not part of this repository. Section numbers refer to that document. Spec version: v1.0 (14 Nov 2026, updated 15 Nov 2026, before any validation run).

Rules:
1. `validation/params.json` is committed **before** the first validation run. The commit hash is written into `validation/out/report.json`.
2. After the first run, no parameter in this section changes. If a mistake is found, make a new version (`v1.1`), keep the old report, and say why in the report. [DESIGN]
3. Every declared tolerance and metric is reported, including bad results. No cherry-picking. [DESIGN]
4. Every number in the report is computed by the program. No hand-typed validation numbers. [SOURCE: project plan §9.4]

### 4.2 Reference path (the Perseverance traverse)
| Field | Value |
| --- | --- |
| Files | `M20_traverse.json` (line segments), `M20_waypoints.json` (points) |
| Primary reference (decision, Nico, 15 Nov 2026) | Mars 2020 Rover PLACES Bundle, `best_interp.csv`, Release 16 (PDS Geosciences Node), posted 2026-08-11, sols 0 to 1897. Page: https://pds-geosciences.wustl.edu/missions/mars2020/places.htm . Downloaded by Austin on 2026-11-15 at 09:42:05 (UTC+8): 8,684,070 bytes, 33,459 lines including the header (33,458 data rows, 28 columns). SHA-256: 58FBC62F2676195A00B40B2DA53A797A70284A8D2344B288C999D325B7CCB4CC . Columns read: `planetocentric_latitude` and `longitude`. Columns not read: `planetodetic_latitude`, easting, northing. 88 rows have `frame` = SITE and all of them have sol = -1; sol 0 appears in a ROVER row. [SOURCE: Austin's report, 2026-11-15] |
| Cross-check reference | `M20_traverse.json` (line segments) and `M20_waypoints.json` (points), the MMGIS files. Downloaded by Austin on 2026-11-15, 08:06 to 08:08 (UTC+8), from the two JSON links listed in `docs/research/vn-perseverance-traverse.md`. Files are in `validation/data/` (commit 0dfc5b6 on the `b-routing` branch) with a `SNAPSHOT.md`. Traverse: 36,661 points, 559 segments, sol 14 to 2022. Waypoints: 708 points, sol 13 to 2022. Neither file has a sol 0. This snapshot replaces an earlier 2026-10-11 snapshot, which is not available as a file. Only this snapshot is used. [SOURCE: Austin's report, 2026-11-15] |
| Source of the MMGIS files | Official page: https://science.nasa.gov/mission/mars-2020-perseverance/location-map/ . That page does not link to the two JSON files (checked by VN). The JSON addresses used are the ones in `docs/research/vn-perseverance-traverse.md`; they were found on third-party pages and are described as such in `docs/CITATIONS.md`. |
| Integrity of the MMGIS files | SHA-256 (from Austin, 2026-11-15). `M20_waypoints.json`: BD143EE69241229926ABD373E6305B8BBB326D6B5A7B4A8D6935262696F93DC4 . `M20_traverse.json`: 6DDD0ECE913D75B45D105946082F95ED84E68F4718B68D32A4421DC30877E7E6 . Also recorded in `docs/CITATIONS.md`. |
| Why PLACES is primary | PLACES is the documented archive release (it supersedes Release 15, sols 0 to 1762, named earlier) [SOURCE: `docs/research/vn-perseverance-traverse.md`]. The MMGIS files are an undocumented live feed, and the snapshot reaches sol 2022, beyond the PLACES release (sol 1897). The two sources agree on the first position: the first traverse vertex (segment 0, vertex 0, sol 14) is latitude 18.44462715, longitude 77.45088573, the same as the first SITE row of PLACES to the digits printed; the distance between the two points is 0.00024 m. [SOURCE: Austin's report, 2026-11-15] The latitude type of the PLACES file is documented, while that of the MMGIS files is not stated in any official document (4.3) [SOURCE: VN]. |
| Partial and duplicate segments (rule fixed by Nico, 15 Nov 2026) [DESIGN] | Applies to the MMGIS cross-check only. **Partial segment:** a traverse segment with fewer than 2 distinct vertices, or a length of 0. The program lists the segments that match. **Duplicate segment:** a segment whose coordinates are identical to the preceding segment; the earlier one is kept. In this snapshot the program finds exactly one duplicate, segment 207 (identical to 206), and segment 206 is a partial segment, so the two rules overlap. The segments removed are the **union** of the two rules, counted once each: 206, 207, 369, 402, 490, which is 5 of 559, leaving 554 (indices are 0-based). The program prints which segments match which rule and the counts. [SOURCE: Austin's report, 2026-11-15] Recorded but **not** used to filter: segments 180 and 181 (same fromRMC and toRMC) and the RMC chain breaks at 83 to 84, 84 to 85, 89 to 90, 95 to 96, 180 to 181 and 534 to 535. The earlier snapshot's "5 partial and 1 duplicate" were counted on a different snapshot (703 points and 556 segments), and the basis of the "703" is not verified (708 is the waypoint count, not the traverse point count); those numbers are not used. [SOURCE: Austin's report, 2026-11-15, for the data; the rule is our own choice] |
| Licence | PLACES: no licence text on the page; the PDS general statement is public domain; the interface specification carries a Caltech copyright notice with government sponsorship acknowledged. MMGIS files: no licence stated; NASA media usage guidelines apply. Recorded in `docs/CITATIONS.md` (columns: Name, Organization, Version, URL, Accessed, License, Used in). |

Later downloads are saved separately and never replace the snapshot above.

### 4.3 Coordinate system and distance
**What the terrain file is.** [SOURCE: USGS label of the full-size file, https://astrogeology.usgs.gov/ckan/dataset/381ba037-d8a9-4cea-86be-374e4951afe3/resource/bd39aeaf-231d-4732-b333-7636bce607ff/download/jez_hirise_soc_006_dtm_molatopography_deltageoid_1m_eqc_latts0_lon0_blend40.lbl ; file and version as downloaded by Xin En on 2026-11-14]
- File: `JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif`, version 006 (taken from the file name), DOI 10.5066/P9REJ9JN.
- Projection: equirectangular, centre longitude 0, centre latitude 0 (the file name says `latTs0`), planetocentric latitude, longitude positive east.
- Planet: a sphere, equatorial radius = polar radius = 3396190 m.
- Pixel size: 1 m in map units. Extent of the full file: latitude 18.3068 to 18.6693, longitude 77.2229 to 77.5840.
- Austin's script reads the CRS and radius from the cropped grid file actually used and confirms they equal the values above. Austin reports (2026-11-15) that they do: sphere with R = 3396190 m, equirectangular, standard parallel 0 and central meridian 0. If they ever differ, stop and tell Nico. [SOURCE: Austin's report; the check is recorded in the `params.json` draft, commit 3d76680]

**The problem with this projection.** With the true-scale latitude at 0, one map metre east-west is shorter on the ground than one map metre north-south, by a factor of cos(latitude), which is about 0.95 at Jezero. Distances measured in raw map metres would overstate east-west distances by about 5%. [DESIGN: decision below]

**Decisions.** [DESIGN]
1. Grid cell centres are converted to latitude/longitude by inverting the DTM projection with the sphere radius above.
2. **All distances are computed in a local azimuthal equidistant projection on the same sphere** (`+proj=aeqd +R=3396190`), centred on the centre of the grid extent, in metres. Never in degrees, and not in raw DTM map metres.
3. The rover path (latitude/longitude) is converted straight into the same local projection.
4. The `18.4663°` easting/northing formula is **not** used. `18.4663°` is the standard parallel of the rover team's PLACES map convention (easting measured at that parallel, northing in true metres; sphere radius 3396190 m) [SOURCE: PLACES SIS v1.0, via `docs/research/vn-perseverance-traverse.md`]. The USGS DTM uses a true-scale latitude of 0. The two differ, so they are never mixed: if PLACES is used, only its planetocentric latitude and longitude columns are read, and they are converted with the sphere of this section.
5. **Mandatory checks, run before validation:**
   - the landing site of 4.4, converted into the DTM projection, falls inside the grid extent;
   - for two points taken from the corners of the extent, the great-circle (haversine) distance on the sphere and the distance in the local projection differ by less than 1%. Print both numbers. If the difference is 1% or more, stop and tell Nico.
   - **Sanity values for the landing site** (first row with `frame` = SITE in the real `best_interp.csv`): planetocentric latitude 18.444627146, longitude 77.450885729. Austin confirmed on 2026-11-15 that the real file's first SITE row has exactly these values, which are also the ones in the PLACES SIS v1.0 example [SOURCE: Austin's report; SIS via VN]. The SIS example lists a planetodetic latitude of 18.346169209, which is lower than the planetocentric one; for Mars at this latitude the planetodetic value should be the larger, so do not use that number. The planetodetic column is not read.
   - **Latitude convention of the rover files.** [SOURCE: `docs/research/vn-perseverance-latitude.md`, checked by VN on 2026-11-15] PLACES `planetocentric_latitude` is planetocentric latitude, computed as the northing divided by the radius 3396190 m, so it is equivalent to a sphere of radius 3396190 m (Rover PLACES SIS v1.0, sections 5.1.3 and 5.2.3; the text of 5.2.3 has a typo, 3393190, in one place). The height datum is the MOLA areoid (SIS 3.9.3). The latitude type and datum of the MMGIS JSON files are **not stated in any official document found** (the NASA MMGIS documentation, the MMGIS GitHub page and NASA's M20 map configuration were checked). The map configuration lists a planetary radius of 3396190 m on both axes, but that is a map setting and does not say what the JSON values are. So in every document the MMGIS latitude is described only as "latitude type not stated in official documentation" and is never labelled planetocentric or planetodetic. For the computation only, the cross-check treats the MMGIS latitude as planetocentric; this is an assumption and the report says so. It affects only the cross-check, because the primary reference is PLACES. [DESIGN] The first MMGIS vertex agrees with the PLACES planetocentric value of the first SITE row to the digits printed (4.2); this is an observation, not documentation. Convert with the sphere above. Using the ellipsoid with b = 3376200 instead would shift points north-south by about 0.2° of latitude, roughly 12 km at 18.5°N (calculated from the two radii, not from a source). That is more than half the height of the grid. Diagnostic: the share of reference points that fall in blocked cells (4.6, item 7). A large share is a warning of a conversion error; report it and tell Nico.
   - **Transform check already run (information only).** Austin's check C (commit de8e1d2, 2026-11-15) converted the MMGIS traverse vertices into the grid. 9,563 vertices fall inside the grid, about 74% fall outside, and 38 of the 9,563 (0.4%) are in blocked cells. This checks the conversion. It is not a comparison of our route with the reference, and it must not be used to tune the slope limit or any other parameter. [SOURCE: Austin's report, 2026-11-15]
6. Distance = planimetric Euclidean distance in the local projection. Point-to-line distance, if used, uses the closest point on the segment.
7. Route length (shown on the web page and used in validation) is computed from route vertex coordinates in the local projection, with one shared function. It is not computed by counting cells.
8. The height reference (`DeltaGeoid` in the file name) does not matter for planimetric distance. If a 3D "surface length" is ever reported, label it separately and state how it was computed.

**Known limitation of the slope data (decision).** The slope script uses a spacing of 1 m on both axes. At Jezero one map metre east-west is about 0.95 m on the ground (cos of latitude 18.5° is about 0.948), so the east-west part of the gradient is understated by about 5%. Decision (Nico, 15 Nov 2026): `slope.npy` is **not** recomputed for v1.0. Reasons: the limitation is documented consistently, features are frozen at 12:00 on 15 Nov, and the 20° limit is already a team heuristic. At the time of this decision no validation number had been produced. [DESIGN]
- The limitation is written in `data/processed/sources.md`, in `grid.json` (`known_issue`), in the HiRISE DTM data card, in the validation report, and on the project page.
- Effect, stated plainly: a slope facing east-west is computed a little lower than it is, so a few cells close to the 20° limit may be treated as passable when a corrected calculation would block them.
- `params.json` records the SHA-256 of `slope.npy` and `grid.json`, so the lock covers the exact terrain data used.
- A corrected slope may be run later only as a separate, labelled "v1.1 sensitivity run" that is declared in `params.json` first. The v1.0 report is kept next to it, and both are reported. [DESIGN]

**Latitude and longitude in the pipeline outputs.** The pipeline scripts used a fallback ellipsoid (`+a=3396190 +b=3376200`) because `EPSG:49900` was not available on the data machine. Since commit 8faffdf (merged to main in pull request #24, confirmed by Xin En) the scripts use the sphere (`+R=3396190`) and `coordinate_notes` in `grid.json` says so. Xin En reports that the top-left latitude/longitude did not change after this, and that `slope.npy`, the layer extents and the routes are unaffected. Those latitude/longitude values stay informational: the web page and the routing code work in projected coordinates. Validation converts the rover's latitude/longitude itself, with the sphere of this section, and does not read them. [DESIGN]

### 4.4 Landing site, first point, last point, and clipping the reference
These rules were fixed on 15 Nov 2026, after reading the snapshot facts and before any comparison of a route with the reference was run. [DESIGN]

Preparing the reference line:
1. The primary reference is built from `best_interp.csv` (4.2). Which rows form the rover path: **[TBD-DATA]** The PLACES Release Notes say that `best_interp.csv` has no `ROVER,n,0` row and that the position at the start of a site is the `SITE,n` row [SOURCE: `docs/research/vn-perseverance-latitude.md`]. Austin's report says a sol 0 row exists among the ROVER rows. The two statements must be reconciled. Austin lists the distinct `frame` values with their row counts, prints the sol 0 row, states which rows form the path, and writes the filter into `params.json`. Nico approves it. SITE rows are not part of the ordered path. Only the first SITE row is used, as the landing site.
2. Order the path by **ascending sol**. Do not trust the order of rows in the file. The script must check that sol never decreases along the line. For the MMGIS cross-check, **[TBD-DATA]** confirm which file carries `sol` (and `dist_total`) for each feature; these field names were only seen on third-party pages.
3. For the MMGIS cross-check, remove the "partial" and "duplicate" segments first, using the rule in 4.2.

Definitions:
- **Landing site and first reference point.** The landing site is the first row of `best_interp.csv` with `frame` = SITE, in file order (planetocentric latitude 18.444627146, longitude 77.450885729). All SITE rows carry sol = -1, so the landing site is recorded with no sol ("n/a, SITE frame") and is not described as sol 0. The MMGIS files have no sol 0 (traverse from sol 14, waypoints from sol 13), so they do not give a touchdown point; their first vertex matches the PLACES landing site (4.2). The program prints the row index, `frame`, sol and coordinates. Do not type coordinates from memory.
- **Extent** = the rectangular bounds of `grid.json`, in the DTM projection of 4.3. A reference point is "inside" if it lies within those bounds.
- **Validation reference** = the first uninterrupted run of the ordered path that is inside the extent, starting at the landing site. If the landing site is outside the extent, stop and ask Nico.
  - Reason: a route needs one continuous reference. If the rover leaves the grid and comes back, the part outside has no terrain data, and the part after re-entry would not connect to the start.
- **First path point** = the landing site.
- **Last path point** = the last vertex of the validation reference before the path first leaves the extent (the largest sol in the run; if two points tie, the one farther along the path). It is a real rover position, not a point where a line crosses the boundary. No boundary-intersection point is created.
- Any part of the path that is inside the extent but after re-entry is **not compared**. The report states its number of points and length.
- The reference is clipped by this rule only. No hand-drawn cuts. The terrain is not cropped here, because `grid.json` is already the cropped terrain made by the data pipeline.
- **Check before locking.** About 74% of the MMGIS vertices are outside the grid (4.3), so the first run inside the extent may be short. **[TBD-DATA]** Austin produces a read-only table: the number of contiguous runs inside the extent, each run's sol range and length, and whether the first run starts at the landing site. The table must not include any comparison with our route. Nico reads it and confirms that the rule above gives a usable reference. If it does not (landing site outside the extent, or a first run too short to be meaningful), stop and tell Nico before locking. A different run is never chosen after seeing results.

The primary reference stops at sol 1897 and the MMGIS cross-check reaches sol 2022. The report states the sol range each one covers.

### 4.5 Metrics, resampling, tolerance, and thresholds
**Resampling.** [DESIGN]
1. Terrain: not resampled. The validation uses `slope.npy` and `grid.json` at their stored resolution.
2. If the grid is ever coarsened, compute slope first at native resolution, then coarsen the **slope** (not the elevation) with the **maximum** per block. A coarse cell is then blocked if any fine cell in it is blocked, which is the cautious choice. Continuous layers use bilinear interpolation; masks and categories use nearest neighbour.
3. Lines: our route and the validation reference are both converted to equally spaced points along their length, spacing = one grid pixel (from `grid.json`), by linear interpolation in the local metre coordinates of 4.3. Never interpolate in degrees. The first and last vertex of each line are always kept exactly; the last step may be shorter than one pixel. The vertices of our route are grid **cell centres** (the path passes through cell centres): cell centre = outer corner of the top-left pixel + (index + 0.5) × pixel size. **[TBD-DATA]** Austin confirms from `grid.json` that `top_left_x_m` and `top_left_y_m` are the outer corner of the top-left pixel (GeoTIFF convention) and not a pixel centre; if they are a centre, the 0.5 is dropped. The reference line is built from its own positions and is not snapped to cell centres.
4. The method and spacing are written into `report.json`.

**Metrics.**

| ID | Metric | Definition |
| --- | --- | --- |
| M0 | Mean and maximum distance (the base numbers) | For each sample on our route, the distance to the nearest sample on the validation reference. Report the mean and the maximum, in metres. Because both lines are sampled one pixel apart, this differs from the true point-to-line distance by at most half a pixel. |
| M1 (primary for the verdict) | Buffer overlap | `overlap_ref` = share of reference length lying within `d_tol` of our route. `overlap_route` = share of our route length lying within `d_tol` of the reference. **M1 = min(overlap_ref, overlap_route).** The minimum stops a very long or very short route from looking good. |
| M2 | Spread of deviation | Median and 95th percentile of the same distances as M0. Report only. |
| M3 | DTW similarity | Dynamic time warping distance between the two sample sequences, divided by the number of points on the warping path, in metres. Report only. |

**Tolerance.** [DESIGN]

| Parameter | Value | Note |
| --- | --- | --- |
| Primary tolerance `d_tol` | 10 m | A round number well above a 1 m cell, so grid steps (up to about 1.4 m on a diagonal) cannot dominate. It is a design choice, not a measured accuracy of any dataset. |
| Sensitivity tolerances | 5 m and 25 m | Always reported next to 10 m, so a reader can see how much the verdict depends on the tolerance. |
| Floor rule | `d_tol` is at least 2 × pixel size | If the pixel size read from `grid.json` breaks this, stop and tell Nico. |

**Run is valid (technical gate).** A run counts as valid only if all of these hold. Otherwise it is reported as `invalid` with the reason, never silently dropped. [DESIGN]
- status is `ok` or `snapped` (4.6)
- total route cost is finite
- no route cell is blocked (4.7)
- snap distance at the start and at the end is at most `r_snap` (4.6)

**Verdict labels** use M1 at `d_tol` = 10 m. They describe closeness; they do not claim the algorithm is "correct". M0, M2 and M3 have no gate, which keeps the number of arbitrary thresholds small. [DESIGN]

| M1 | Label |
| --- | --- |
| at least 0.80 | close match |
| at least 0.50 and below 0.80 | partial match |
| below 0.50 | weak match |

Also report `end_point_error_m`: the distance between our route's first/last point and the reference's first/last point (information only). Because our route starts and ends at cell centres, this includes an offset of up to about 0.71 pixel (half the cell diagonal).

### 4.6 Endpoints and "unreachable" for validation
This section applies to the **validation** route only. POI routes follow section 3 (no fallback endpoint).

1. The start and end cells are the grid cells containing the first and last path points of 4.4.
2. If either cell is blocked, move it to the nearest unblocked cell within `r_snap` = 3 cells. The run is marked `snapped` and the snap distance is stored. [DESIGN] (Set `r_snap` to 0 to turn snapping off.)
3. If no unblocked cell exists within `r_snap`, the status is `unreachable_endpoint`.
4. If both ends are fine but no path of finite cost exists, the status is `unreachable`.
5. For any `unreachable*` status the metrics are `null`. The run counts as **failed** in the summary table and is never removed from the report.
6. The program must not retry with a higher slope limit. Any relaxed-limit run has to be declared in `params.json` in advance and labelled "relaxed limit" in every table. [DESIGN]
7. Always record this diagnostic: the share of reference-path points that fall in cells our rule blocks. If the rover drove through terrain we call impassable, that is a finding about our slope limit. Report it honestly. [DESIGN]

### 4.7 Blocked cells (infinite cost)
1. Blocked means `cost = np.inf`. Do **not** use a large finite number such as 1e9: the path could cross a blocked cell and still return a finite-looking answer. [DESIGN]
2. A cell is blocked if its slope is above the limit in section 2, or its slope is NaN or nodata (section 2). [DESIGN]
3. The HiRISE confidence layer (project plan §7.1) is not used in v1. Mention this as a limitation in the report. [DESIGN]
4. Moves: 8-neighbour with geometric step lengths (diagonal = √2), as in section 3. Corner-cutting between two blocked neighbours is a known limitation of this method and is stated in `routing/README.md`. [DESIGN]
5. Required tests (Austin):
   - a wall of blocked cells across the grid gives `unreachable`;
   - a grid with one open gap routes through the gap;
   - after every run, assert that the total cost is finite and that no route cell is blocked.

### 4.8 Parameters (locked before running)
Committed in `validation/params.json` before the first validation run and not changed afterwards:
- slope limit: 20 degrees
- cost formula: `1 + (slope / limit)^2`
- connectivity: `fully_connected=True`, `geometric=True`
- pixel size and grid extent: read from `grid.json`
- resampling spacing: one grid pixel; route vertices at cell centres; first and last vertex kept
- blocked cells: `np.inf`; NaN or nodata is blocked
- tolerances: `d_tol` = 10 m, sensitivity 5 m and 25 m
- verdict thresholds on M1: 0.80 and 0.50
- `r_snap` = 3 cells
- primary reference file (PLACES `best_interp.csv`): name, download time, size, line count, SHA-256, columns read (4.2); cross-check files: exact names, download time and SHA-256 (4.2), recorded in the report
- SHA-256 of `slope.npy` and `grid.json`
- the rule and counts for "partial" and "duplicate" segments in the MMGIS cross-check (4.2), the landing-site rule, the rover-row filter and the first/last point rule (4.4)
- terrain file and version, DTM projection, and the local distance projection with its 1% check (4.3)

### 4.9 Comparison segment and caveat
- Comparison segment: the validation reference of 4.4 (the first uninterrupted run of the Perseverance path inside the extent of `grid.json`, starting at the landing site). Parts of the path outside the grid, and parts after re-entry, are not compared.
- Caveat: the rover traverse is not the optimal route for a person on foot. The comparison is a sanity check, not ground truth. Results are reported as they are, good or bad.

## 5. Comparison routes (F10)
- Data layer removed in each comparison: one comparison route per layer listed in `data/processed/layers/layers.json`, each with that single layer removed from the cost inputs. Output file name: `route_<name>_no_<layer>.geojson`.
- Only layers that `routing/config.json` declares as cost inputs can change a route. Layers that are not cost inputs are listed in the report as "no effect on routing".

## 6. Open items

- Austin's list has 9 items. His first message said 10 but numbered only 9; on 15 Nov 2026 Nico and Austin agreed that there is no item 10.
- **[TBD-DATA]** values still open before `validation/params.json` is locked: 4.4 (the rover-row filter, the `sol` and `dist_total` field names, and the table of runs inside the extent) and 4.5 (the cell-centre convention of `grid.json`).
- Already settled (15 Nov 2026): primary reference and its hash (4.2), landing site rule (4.4), partial and duplicate rule (4.2), slope not recomputed (4.3), latitude convention of the PLACES file and the undocumented MMGIS latitude type (4.3), the CRS of the grid (4.3), 0-based segment indices (4.2), and the polyline and resampling rule (4.5).

Where Austin's items are answered:

| # | Item | Section |
| --- | --- | --- |
| 1 | Tolerance and pass/fail thresholds | 4.5 |
| 2 | Perseverance file name, version, download date | 4.2 |
| 3 | Resampling method | 4.5 |
| 4 | Distance algorithm and coordinate system | 4.3 |
| 5 | Definition of the landing site | 4.4 |
| 6 | "Unreachable" rule in validation | 4.6 |
| 7 | Blocked cells (infinite cost) | 4.7 |
| 8 | Meaning of "last path point" | 4.4 |
| 9 | Cropping the Perseverance path | 4.4 |

## 7. Suggested `params.json` keys (cross-check)
Austin may rename the keys. Every line must exist in some form. `null` values are **[TBD-DATA]**.

```json
{
  "spec_version": "v1.0",
  "reference": {
    "primary_file": "best_interp.csv",
    "primary_release": "PLACES Release 16",
    "primary_download_time": "2026-11-15 09:42:05 UTC+8",
    "primary_bytes": 8684070,
    "primary_lines_including_header": 33459,
    "sha256_primary": "58FBC62F2676195A00B40B2DA53A797A70284A8D2344B288C999D325B7CCB4CC",
    "primary_columns_used": ["planetocentric_latitude", "longitude"],
    "primary_path_row_filter": null,
    "cross_check_traverse_file": "M20_traverse.json",
    "cross_check_waypoints_file": "M20_waypoints.json",
    "cross_check_download_time": "2026-11-15 08:06-08:08 UTC+8",
    "traverse_points": 36661,
    "traverse_segments": 559,
    "min_sol_in_traverse": 14,
    "max_sol_in_traverse": 2022,
    "waypoints_count": 708,
    "min_sol_in_waypoints": 13,
    "max_sol_in_waypoints": 2022,
    "sha256_traverse": "6DDD0ECE913D75B45D105946082F95ED84E68F4718B68D32A4421DC30877E7E6",
    "sha256_waypoints": "BD143EE69241229926ABD373E6305B8BBB326D6B5A7B4A8D6935262696F93DC4",
    "sha256_slope_npy": null,
    "sha256_grid_json": null,
    "partial_rule": "fewer than 2 distinct vertices, or length 0",
    "duplicate_rule": "coordinates identical to the preceding segment; keep the earlier",
    "partial_segments": null,
    "duplicate_segments": [207],
    "removed_segments_union": [206, 207, 369, 402, 490],
    "removed_segments_union_count": 5,
    "segment_index_base": 0,
    "recorded_not_filtered": { "same_fromRMC_toRMC": [180, 181], "rmc_chain_breaks": ["83-84", "84-85", "89-90", "95-96", "180-181", "534-535"] }
  },
  "clip": { "extent": "grid.json bounds", "reference_run": "first uninterrupted run inside the extent, starting at the landing site", "landing_site": "first row with frame == SITE in best_interp.csv", "landing_site_sol": null },
  "crs": {
    "terrain_file": "JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif",
    "terrain_version": "006",
    "dtm_projection": "equirectangular, lat_ts 0, lon_0 0, sphere (confirmed by Austin, 2026-11-15)",
    "radius_m": 3396190,
    "mmgis_latitude_treatment": "assumed planetocentric for the cross-check only; documents say: latitude type not stated in official documentation",
    "distance_projection": "aeqd, same sphere, centred on grid extent centre",
    "haversine_check_max_relative_difference": 0.01
  },
  "resampling": { "terrain": "none", "coarsen_slope_by": "max", "line_spacing": "one grid pixel", "route_vertices": "cell_centres", "keep_first_last_vertex": true },
  "cost": { "formula": "1 + (slope / limit)^2", "slope_limit_deg": 20, "blocked_value": "inf", "nan_is_blocked": true, "fully_connected": true, "geometric": true },
  "tolerance_m": { "primary": 10, "sensitivity": [5, 25] },
  "snap": { "r_snap_cells": 3 },
  "metrics": ["mean_max_distance", "buffer_overlap_min", "median_p95", "dtw_per_step"],
  "verdict_thresholds_M1": { "close": 0.80, "partial": 0.50 }
}
```
