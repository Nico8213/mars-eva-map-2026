# Requirements Document

## Introduction

This feature adds a least-cost path tool under `routing/`. The tool reads a slope raster (`data/processed/slope.npy`) and its grid description (`data/processed/grid.json`), takes a start point and an end point, and writes one GeoJSON route file (`routing/out/route_<name>.geojson`). The cost function, slope limit, and connectivity come only from `routing/config.json`, and each value in that file records its basis (source). The tool is first exercised on a synthetic slope map generated under `routing/test_data/`. Formats follow `docs/INTERFACES.md`. The cost values are a relative cost ranking, not a validated human EVA model. This spec does not compute or write any validation numbers.

Out of scope: comparison routes (`route_<name>_no_<layer>.geojson`), validation against the Perseverance traverse, and any validation metric.

## Glossary

- **Router**: The command-line script in `routing/` that computes a least-cost path and writes the GeoJSON route file.
- **Config_File**: The file `routing/config.json`, the only source of cost function parameters, slope limit, and connectivity.
- **Slope_Raster**: The 2D float32 array in `slope.npy`, in degrees, with NaN for missing cells, shape (height, width).
- **Grid_File**: The file `grid.json`, which describes the raster grid (`pixel_size_m`, `width`, `height`, `top_left` with `easting_m` and `northing_m`, `crs`, `nodata_value`).
- **Cost_Raster**: A 2D array of per-cell traversal costs derived from the Slope_Raster using the Config_File.
- **Blocked_Cell**: A cell with infinite cost, because its slope is NaN or exceeds the slope limit.
- **Slope_Limit**: The maximum slope in degrees, read from the Config_File, above which a cell is a Blocked_Cell.
- **Endpoint**: A start or end location, given either as a grid pixel (row, col) or as projected coordinates (easting_m, northing_m) in the Grid_File CRS.
- **POI_ID**: An optional text identifier of a point of interest, copied into the route properties `start_poi` or `end_poi`.
- **Route_File**: The output file `routing/out/route_<name>.geojson`, one GeoJSON Feature with a LineString geometry.
- **Test_Data_Generator**: The script under `routing/test_data/` that writes a synthetic slope.npy and grid.json.
- **Synthetic_Data**: The slope.npy and grid.json files written by the Test_Data_Generator.
- **Unreachable**: The result when an Endpoint is a Blocked_Cell, an Endpoint is outside the grid, or no path exists between the Endpoints.

## Requirements

### Requirement 1: Configuration file with documented bases

**User Story:** As a team member, I want all cost parameters in one documented config file, so that the parameters are fixed before running and every number has a stated source.

#### Acceptance Criteria

1. WHEN the Router starts a run, THE Router SHALL read the cost function type, the cost function parameters, the Slope_Limit, and the connectivity only from the Config_File, and SHALL complete reading the Config_File before processing any cell.
2. THE Config_File SHALL contain, for each parameter, a value field and a basis field, where the basis field is a non-empty string that states the source, the version, and the date (in YYYY-MM-DD format) of that value.
3. THE Config_File SHALL record, in the basis field of the Slope_Limit, that the Slope_Limit of 20 degrees is a team choice referenced to a rover limit (Perseverance, JPL document https://robotics.jpl.nasa.gov/media/documents/2026_RO_AAS_final.pdf) and is not a human or spacesuit limit.
4. THE Config_File SHALL record, in the basis field of the cost function, that the quadratic cost form is a transparent heuristic not fitted to data, qualitatively consistent with Minetti et al. 2002 (https://iris.unibs.it/handle/11379/540545), measured under Earth gravity, and that results are a relative cost ranking only.
5. THE Config_File SHALL define the per-cell cost as 1 + (slope / Slope_Limit)^2 with slope in degrees, with Slope_Limit equal to 20 degrees, and the connectivity as 8-neighbour.
6. IF the Config_File is missing, is not valid JSON, or lacks a required parameter, value field, or basis field, THEN THE Router SHALL exit with a non-zero status, print an error message that names the missing file or the missing item, and write no output files.
7. IF a parameter value in the Config_File is not a finite number greater than 0 (for Slope_Limit and numeric cost parameters), or the connectivity is not a supported value, THEN THE Router SHALL exit with a non-zero status and print an error message that names the invalid parameter and the rejected value.
8. THE Router SHALL contain no cost function constants or slope limit values outside the Config_File, and a change to any such value in the Config_File SHALL change the Router's computed costs without any change to the Router's source code.

### Requirement 2: Input loading and validation

**User Story:** As a routing analyst, I want the tool to check its inputs, so that a route is never computed from mismatched or malformed data.

#### Acceptance Criteria

1. WHEN the Router is run, THE Router SHALL accept the paths to the Slope_Raster file, the Grid_File, and the Config_File as command-line arguments, with defaults `data/processed/slope.npy`, `data/processed/grid.json`, and `routing/config.json`.
2. WHEN the Slope_Raster and Grid_File are loaded, THE Router SHALL verify that the Slope_Raster has exactly 2 dimensions and that its shape equals (height, width) from the Grid_File.
3. IF the Slope_Raster file, the Grid_File, or the Config_File does not exist or cannot be read, THEN THE Router SHALL exit with a non-zero status, print an error message that names the missing or unreadable file, and write no route output files.
4. IF the Slope_Raster has a number of dimensions other than 2, THEN THE Router SHALL exit with a non-zero status, print an error message that states the actual number of dimensions, and write no route output files.
5. IF the Slope_Raster shape does not equal (height, width) from the Grid_File, THEN THE Router SHALL exit with a non-zero status, print an error message that states both shapes, and write no route output files.
6. IF the Grid_File lacks `pixel_size_m`, `width`, `height`, `top_left`, or `crs`, THEN THE Router SHALL exit with a non-zero status, print an error message that names every missing field, and write no route output files.
7. IF the Slope_Raster file or the Grid_File exists but cannot be parsed (for example, invalid JSON or a file that is not a valid NumPy array), THEN THE Router SHALL exit with a non-zero status, print an error message that names the file and states that it is malformed, and write no route output files.
8. IF `pixel_size_m` is not a number greater than 0, or `width` or `height` is not an integer greater than 0, THEN THE Router SHALL exit with a non-zero status, print an error message that names the invalid field and its value, and write no route output files.

### Requirement 3: Cost raster construction

**User Story:** As a routing analyst, I want slope converted to traversal cost by the configured function, so that steeper terrain costs more and impassable terrain is excluded.

#### Acceptance Criteria

1. WHEN the Router builds the Cost_Raster, THE Router SHALL compute, for each Slope_Raster cell, an unsigned slope equal to the absolute value of the cell's slope, in degrees.
2. WHEN a Slope_Raster cell has a finite unsigned slope less than or equal to the Slope_Limit, THE Router SHALL set the corresponding Cost_Raster cell to 1 + (unsigned slope / Slope_Limit)^2, using the Slope_Limit value from the Config_File, so that a cell with slope 0 has cost 1.0 and a cell with slope equal to the Slope_Limit has cost 2.0.
3. WHEN a Slope_Raster cell has a finite unsigned slope strictly greater than the Slope_Limit, THE Router SHALL mark the corresponding cell as a Blocked_Cell.
4. WHEN a Slope_Raster cell is NaN, THE Router SHALL mark the corresponding cell as a Blocked_Cell.
5. WHEN the Router passes the Cost_Raster to the path search, THE Router SHALL represent every Blocked_Cell as infinite cost, and no Blocked_Cell SHALL appear in any returned path.
6. IF the Slope_Limit in the Config_File is missing, non-numeric, less than or equal to 0, or NaN, THEN THE Router SHALL abort Cost_Raster construction, report an error naming the invalid Slope_Limit, and produce no Cost_Raster output.
7. THE Router SHALL produce a Cost_Raster with the same number of rows, columns, and cell positions as the Slope_Raster, with every non-blocked cell holding a finite value from 1.0 to 2.0 inclusive.

### Requirement 4: Endpoint specification

**User Story:** As a routing analyst, I want to give start and end points in grid or projected coordinates, so that I can route between map locations or pixels.

#### Acceptance Criteria

1. WHEN start and end are given as grid pixels, THE Router SHALL interpret each Endpoint as (row, col) of the Slope_Raster, where row and col are zero-based integers, row 0 is the top row, and col 0 is the leftmost column.
2. WHEN start and end are given as projected coordinates, THE Router SHALL convert each Endpoint to a pixel using col = floor((easting_m - top_left.easting_m) / pixel_size_m) and row = floor((top_left.northing_m - northing_m) / pixel_size_m), where all quantities are in metres.
3. WHERE a POI_ID is given for the start or the end, THE Router SHALL copy the POI_ID unchanged into `start_poi` or `end_poi` of the Route_File properties.
4. WHEN no POI_ID is given for the start or the end, THE Router SHALL set the corresponding `start_poi` or `end_poi` property of the Route_File to null.
5. IF an Endpoint is outside the grid, meaning row < 0, row >= the Slope_Raster row count, col < 0, or col >= the Slope_Raster column count, THEN THE Router SHALL report Unreachable, identify which Endpoint (start or end) is outside the grid, exit with a non-zero status, and write no Route_File.
6. IF the start or end is given in both grid pixel and projected coordinate form, THEN THE Router SHALL exit with a non-zero status, print an error message stating that exactly one form is required for each Endpoint, and write no Route_File.
7. IF an Endpoint value is missing, non-numeric, or not finite (NaN or infinity), THEN THE Router SHALL exit with a non-zero status, print an error message identifying the invalid Endpoint and value, and write no Route_File.

### Requirement 5: Least-cost path search

**User Story:** As a routing analyst, I want the least-cost path between two points over the cost raster, so that the route avoids steep and blocked terrain.

#### Acceptance Criteria

1. WHEN both Endpoints are valid, non-blocked cells, THE Router SHALL compute the least-cost path using `skimage.graph.route_through_array` with the connectivity from the Config_File and geometric path-length weighting, and SHALL return an ordered list of cells that begins at the start Endpoint and ends at the end Endpoint.
2. WHEN the start and end Endpoints are the same non-blocked cell, THE Router SHALL write a Route_File with a LineString of that single cell centre and `length_m` equal to 0.
3. IF an Endpoint is a Blocked_Cell, THEN THE Router SHALL report Unreachable with a message that names which Endpoint (start, end, or both) is blocked.
4. IF both Endpoints are non-blocked cells and no path of non-blocked cells connects them under the configured connectivity, THEN THE Router SHALL report Unreachable with a message indicating that no path exists.
5. IF Unreachable is reported, THEN THE Router SHALL exit with a non-zero status, write no Route_File, and not substitute any other cell for an Endpoint.
6. FOR ALL pairs of valid Endpoints for which a path is returned, THE Router SHALL return a path in which every cell is non-blocked and every consecutive pair of cells are neighbours under the configured connectivity (path validity property).
7. FOR ALL pairs of valid Endpoints for which a path exists, THE Router SHALL return paths whose total costs differ by no more than 1e-6 (relative) when the start and end Endpoints are swapped (symmetry property).

### Requirement 6: GeoJSON route output

**User Story:** As a web map developer, I want a standard GeoJSON route file with the properties defined in INTERFACES.md, so that the web viewer can display and describe the route.

#### Acceptance Criteria

1. WHEN a path is found, THE Router SHALL write `routing/out/route_<name>.geojson` containing exactly one GeoJSON Feature with a LineString geometry, where `<name>` is given by a command-line argument and contains 1 to 64 characters from the set A-Z, a-z, 0-9, hyphen, and underscore.
2. IF the `<name>` argument is missing or contains a character outside the permitted set or exceeds 64 characters, THEN THE Router SHALL write no Route_File, print an error message indicating the invalid or missing name, and exit with a non-zero status.
3. THE Router SHALL write each LineString coordinate as the pixel centre in projected metres in the Grid_File CRS, with easting = top_left.easting_m + (col + 0.5) * pixel_size_m and northing = top_left.northing_m - (row + 0.5) * pixel_size_m, in path order from start to end. A single-cell route (Requirement 5, criterion 2) is the only case with fewer than 2 coordinates.
4. THE Router SHALL write the properties `name`, `start_poi`, `end_poi`, `length_m`, `max_slope_deg`, `slope_threshold_deg`, `data_used`, `cost_function`, and `generated_from`.
5. THE Router SHALL set `name` to the `<name>` command-line argument.
6. THE Router SHALL set `length_m` to the sum of the Euclidean distances between consecutive LineString coordinates, in metres, rounded to 0.01 m.
7. THE Router SHALL set `max_slope_deg` to the maximum Slope_Raster value among the path cells, in degrees, rounded to 0.01 degrees.
8. THE Router SHALL set `slope_threshold_deg` to the Slope_Limit from the Config_File, in degrees.
9. THE Router SHALL set `data_used` to an array of layer ids, containing `slope` for this feature.
10. THE Router SHALL set `cost_function` to a text string of 1 to 500 characters naming the cost function and listing each parameter name and value read from the Config_File.
11. THE Router SHALL set `generated_from` to the git commit hash and the Config_File content used.
12. WHERE no POI_ID is given for the start or end point, THE Router SHALL set the corresponding `start_poi` or `end_poi` property to null.
13. IF the `routing/out/` directory does not exist, THEN THE Router SHALL create it before writing the Route_File.
14. WHEN the Route_File is written, THE Router SHALL print exactly one line containing the file path and the file size in bytes.
15. FOR ALL routes written, parsing the Route_File then reading its LineString coordinates and converting each to a pixel SHALL reproduce the path cells in the same order, with row and col each matching exactly (round-trip property).
16. IF the git commit hash cannot be determined, THEN THE Router SHALL set the commit hash in `generated_from` to the text `unknown` and continue.
17. IF the Route_File cannot be written (for example, the directory is not writable or the disk is full), THEN THE Router SHALL print an error message indicating the write failure and the file path, leave no partial Route_File at that path, and exit with a non-zero status.

### Requirement 7: Synthetic test data

**User Story:** As a developer, I want a fake slope map and grid file, so that I can test the Router before the real data exists.

#### Acceptance Criteria

1. WHEN the Test_Data_Generator is run with a valid seed argument, THE Test_Data_Generator SHALL write `slope.npy` as a 2D float32 array with finite values in the range 0.0 to 90.0 degrees (NaN cells excepted) and `grid.json` into `routing/test_data/`, and SHALL create `routing/test_data/` if it does not exist.
2. WHEN the Test_Data_Generator writes the Grid_File, THE Test_Data_Generator SHALL include `pixel_size_m` (number greater than 0), `width` (integer from 1 to 1024), `height` (integer from 1 to 1024), `top_left` (object with `easting_m` and `northing_m`, as in docs/INTERFACES.md), `crs` (non-empty string), and `nodata_value` (number or null), with the Slope_Raster shape equal to (height, width).
3. WHEN the Test_Data_Generator writes the Slope_Raster, THE Test_Data_Generator SHALL include at least one contiguous flat region of at least 10 cells with all values at or below 1.0 degree, at least one contiguous region of at least 10 cells with all values greater than the Slope_Limit, and at least one NaN cell.
4. WHEN the Test_Data_Generator is run twice with identical arguments, including the seed, THE Test_Data_Generator SHALL produce `slope.npy` and `grid.json` files that are byte-for-byte identical between the two runs.
5. THE Test_Data_Generator SHALL set the `crs` value in the Grid_File to a string containing the word "SYNTHETIC" and SHALL include a top-level `synthetic` field with the value `true` in the Grid_File.
6. WHEN the Test_Data_Generator finishes writing a file, THE Test_Data_Generator SHALL print exactly one line to standard output for that file, containing the file path and the file size in bytes.
7. THE Test_Data_Generator SHALL keep each written file under 50 MB (52,428,800 bytes).
8. IF the seed argument is missing or is not an integer, or if `routing/test_data/` cannot be written, THEN THE Test_Data_Generator SHALL exit with a non-zero status, print an error message indicating the cause, and leave any previously existing `slope.npy` and `grid.json` unchanged.

### Requirement 8: Tests on synthetic data

**User Story:** As a developer, I want automated tests that use only synthetic data, so that the Router behaviour is checked without real data and without invented validation numbers.

#### Acceptance Criteria

1. THE test suite SHALL build every input grid from Synthetic_Data or from arrays defined inside the test code, with each array no larger than 100 rows by 100 columns, and SHALL NOT read any file from `data/processed/`.
2. THE test suite SHALL include a test in which a steep ridge row, with every cell slope above the Slope_Limit, spans the full grid width except for one gap cell. The start Endpoint and end Endpoint are on opposite sides of the ridge. The test SHALL assert that the Router reports success and that the returned path contains the gap cell and no cell with slope above the Slope_Limit.
3. THE test suite SHALL include a test in which a full-width ridge, with every cell slope above the Slope_Limit, separates the start Endpoint from the end Endpoint. The test SHALL assert that the Router reports Unreachable and that no Route_File exists in the output location after the run.
4. THE test suite SHALL include a test for each Endpoint (start and end) in which that Endpoint is on a NaN cell. The test SHALL assert that the Router reports Unreachable and that no Route_File exists in the output location after the run.
5. THE test suite SHALL include a test in which a cell with slope exactly equal to the Slope_Limit is traversable, and a cell with slope greater than the Slope_Limit by the smallest step used in the test data is blocked. The test SHALL assert both outcomes on the same grid.
6. THE test suite SHALL include a test on a grid of at most 5 rows by 5 columns that compares the Route_File properties and LineString coordinates against a hand-computed expected route. Coordinates SHALL match exactly, or within an absolute tolerance of 1e-9 m for floating-point values. The expected values SHALL be written in the test as literals.
7. THE test suite SHALL include a test that runs the Router twice on the same grid with two temporary Config_Files differing only in the Slope_Limit value. The test SHALL assert that the two routes differ, in path or in Unreachable status, in the direction the Slope_Limit change predicts. The test SHALL NOT modify the default Config_File.
8. THE test suite SHALL NOT contain any assertion that compares a numeric result to a validation reference value.

### Requirement 9: Command-line behaviour and constraints

**User Story:** As a team member, I want the tools to follow project conventions, so that they run reproducibly from the command line.

#### Acceptance Criteria

1. THE Router SHALL run on Python 3.12 or newer using numpy and scikit-image.
2. THE Router SHALL run from the command line without opening any graphical window or prompting for interactive input, and SHALL write results only to files.
3. THE Router SHALL write output files only under `routing/out/` and THE Test_Data_Generator SHALL write output files only under `routing/test_data/`.
4. IF an output file would be 50 MB (52,428,800 bytes) or larger, THEN THE Router SHALL stop writing that file, exit with a non-zero status, and print an error message identifying the file and the size limit.
5. WHEN the command-line arguments are invalid or incomplete, THE Router SHALL exit with a non-zero status, print a usage message listing the required and optional arguments to standard error, and write no files under `routing/out/`.
6. WHEN the Router completes all requested outputs, THE Router SHALL exit with status 0.
7. THE Router SHALL NOT compute or write validation metrics or comparison routes.