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

"Project plan" means the team's internal planning document. It is not part of this repository. Section numbers refer to that document. Spec version: v1.0 (14 Nov 2026).

Rules:
1. `validation/params.json` is committed **before** the first validation run. The commit hash is written into `validation/out/report.json`.
2. After the first run, no parameter in this section changes. If a mistake is found, make a new version (`v1.1`), keep the old report, and say why in the report. [DESIGN]
3. Every declared tolerance and metric is reported, including bad results. No cherry-picking. [DESIGN]
4. Every number in the report is computed by the program. No hand-typed validation numbers. [SOURCE: project plan §9.4]

### 4.2 Reference path (the Perseverance traverse)
| Field | Value |
| --- | --- |
| Files | `M20_traverse.json` (line segments), `M20_waypoints.json` (points) |
| Snapshot used | 2026-10-11 snapshot, last sol 1980 [SOURCE: project plan §7.4; §7.6 says validation uses only this snapshot] |
| Download date | 2026-10-11 [SOURCE: project plan §7.4]. **[TBD-DATA]** confirm against the file's timestamp in `validation/data/`. |
| Source | Official page: https://science.nasa.gov/mission/mars-2020-perseverance/location-map/ . Direct JSON addresses used by several public projects (found on third-party pages, not on an official NASA document): `https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_traverse.json` and `.../M20_waypoints.json`. They must be checked before use. VN provides the final source link, and the small files go in `validation/data/`. |
| Integrity | **[TBD-DATA]** SHA-256 of both files. Windows: `certutil -hashfile <file> SHA256`. Mac/Linux: `shasum -a 256 <file>`. Write both hashes here and in `docs/CITATIONS.md`. |
| Counts to re-check | 703 points, 556 segments. Before computing any length, remove 5 partial segments and 1 duplicate segment [SOURCE: project plan §7.4, Decisions log #3]. **[TBD-DATA]** the script prints the counts; they must match. |
| Authoritative citation | PLACES, Release 15, sols 0–1762 [SOURCE: project plan §7.4]. |
| Licence | **[TBD-DATA]** record what NASA states for this data in `docs/CITATIONS.md` (columns: Name, Organization, Version, URL, Accessed, License, Used in). |

New downloads are saved separately and never replace the 2026-10-11 snapshot (project plan §7.6).

### 4.3 Coordinate system and distance
1. **All distances are computed in a projected metre CRS, never in degrees.** [DESIGN]
2. The CRS is the one stored in the HiRISE DTM file (read with `rasterio`/`pyproj`), or in `grid.json` if it carries the same information. The planet radius and projection parameters are read from the same place. Do not hard-code them. **[TBD-DATA]** write the CRS string and radius found there.
3. The rover path (latitude/longitude) is reprojected into that CRS. The `18.4663°` easting/northing formula is **not** used for validation. Project plan §8.2 and §12.6 list the standard-parallel mismatch as open. [SOURCE: project plan §8.2]
4. **Consistency check (mandatory, runs before validation):** project the first waypoint with both methods and print the offset in metres. If the offset is larger than `d_tol / 2` = 5 m, stop and tell Nico. Do not "fix" the formula. [DESIGN]
5. Distance = planimetric Euclidean distance in the projected plane. [DESIGN]
6. The height reference (`elev_geoid`) does not matter for planimetric distance. If a 3D "surface length" is ever reported, label it separately and state how it was computed. [DESIGN]
7. Route length shown on the webpage and length used in validation come from the same function. [DESIGN]

### 4.4 Landing site, first point, last point, and clipping the traverse
Preparing the reference line:
1. Remove the 5 partial segments and 1 duplicate segment first (4.2). [SOURCE: project plan §7.4]
2. Order everything by **ascending sol**. Do not trust the order of features in the file. The script must check that sol never decreases along the line. **[TBD-DATA]** confirm which file carries `sol` (and `dist_total`) for each feature; these field names were only seen on third-party pages. [DESIGN]

Definitions:
- **Landing site** = the point with the smallest sol in `M20_waypoints.json`. It should be sol 0, the touchdown location, commonly called "Octavia E. Butler Landing". **[TBD-DATA]** the script prints sol, index and coordinates; copy them here. If the smallest sol is not 0, stop and ask Nico. [DESIGN]
- **Extent** = the rectangular bounds of `grid.json`, in the CRS of 4.3. A traverse point is "inside" if it lies within those bounds. [DESIGN]
- **Validation reference** = the first uninterrupted run of the ordered traverse that is inside the extent, starting at the landing site. If the landing site is outside the extent, stop and ask Nico. [DESIGN]
  - Reason: a route needs one continuous reference. If the rover leaves the grid and comes back, the part outside has no terrain data, and the part after re-entry would not connect to the start.
- **First path point** = the landing site.
- **Last path point** = the last vertex of the validation reference before the traverse first leaves the extent (the largest sol in the run; if two points tie, the one farther along the path, for example the larger `dist_total`). It is a real rover position, not a point where a line crosses the boundary. No boundary-intersection point is created. [DESIGN]
- Any part of the traverse that is inside the extent but after re-entry is **not compared**. The report states its number of points and length. [DESIGN]
- The traverse is clipped by this rule only. No hand-drawn cuts. The terrain is not cropped here, because `grid.json` is already the cropped terrain made by the data pipeline.

If the validation reference lies mostly at sols above 1762, say so in the report, because PLACES Release 15 stops at sol 1762 (4.2). [DESIGN]

### 4.5 Metrics, resampling, tolerance, and thresholds
**Resampling.** [DESIGN]
1. Terrain: not resampled. The validation uses `slope.npy` and `grid.json` at their stored resolution.
2. If the grid is ever coarsened, compute slope first at native resolution, then coarsen the **slope** (not the elevation) with the **maximum** per block. A coarse cell is then blocked if any fine cell in it is blocked, which is the cautious choice. Continuous layers use bilinear interpolation; masks and categories use nearest neighbour.
3. Lines: our route and the validation reference are both converted to equally spaced points along their length, spacing = one grid pixel (from `grid.json`), by linear interpolation in the projected metre coordinates of 4.3. Never interpolate in degrees.
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

Also report `end_point_error_m`: the distance between our route's first/last point and the reference's first/last point (information only).

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
- resampling spacing: one grid pixel
- blocked cells: `np.inf`; NaN or nodata is blocked
- tolerances: `d_tol` = 10 m, sensitivity 5 m and 25 m
- verdict thresholds on M1: 0.80 and 0.50
- `r_snap` = 3 cells
- traverse files: exact names, snapshot date, download date and SHA-256 (4.2), recorded in the report
- CRS source and consistency-check limit (4.3)

### 4.9 Comparison segment and caveat
- Comparison segment: the validation reference of 4.4 (the first uninterrupted run of the Perseverance traverse inside the extent of `grid.json`, starting at the landing site). Parts of the traverse outside the grid, and parts after re-entry, are not compared.
- Caveat: the rover traverse is not the optimal route for a person on foot. The comparison is a sanity check, not ground truth. Results are reported as they are, good or bad.

## 5. Comparison routes (F10)
- Data layer removed in each comparison: one comparison route per layer listed in `data/processed/layers/layers.json`, each with that single layer removed from the cost inputs. Output file name: `route_<name>_no_<layer>.geojson`.
- Only layers that `routing/config.json` declares as cost inputs can change a route. Layers that are not cost inputs are listed in the report as "no effect on routing".

## 6. Open items

- **Item 10 from Austin's list:** **[TBD, ask Austin]** (his message said 10 items but numbered only 9).
- All **[TBD-DATA]** values in 4.2, 4.3 and 4.4 must be filled from the real files before `validation/params.json` is locked.

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
    "traverse_file": "M20_traverse.json",
    "waypoints_file": "M20_waypoints.json",
    "snapshot_date": "2026-10-11",
    "last_sol_in_file": 1980,
    "sha256_traverse": null,
    "sha256_waypoints": null,
    "remove_partial_segments": 5,
    "remove_duplicate_segments": 1
  },
  "clip": { "extent": "grid.json bounds", "reference_run": "first uninterrupted run from landing site", "landing_site": "min sol in waypoints, expected sol 0" },
  "crs": { "source": "HiRISE DTM file metadata", "crs_string": null, "radius_m": null, "consistency_check_max_offset_m": 5 },
  "resampling": { "terrain": "none", "coarsen_slope_by": "max", "line_spacing": "one grid pixel" },
  "cost": { "formula": "1 + (slope / limit)^2", "slope_limit_deg": 20, "blocked_value": "inf", "nan_is_blocked": true, "fully_connected": true, "geometric": true },
  "tolerance_m": { "primary": 10, "sensitivity": [5, 25] },
  "snap": { "r_snap_cells": 3 },
  "metrics": ["mean_max_distance", "buffer_overlap_min", "median_p95", "dtw_per_step"],
  "verdict_thresholds_M1": { "close": 0.80, "partial": 0.50 }
}
```
