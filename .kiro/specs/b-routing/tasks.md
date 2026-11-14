# Implementation Plan: b-routing

## Overview

Implementation language: Python 3.12 or newer (numpy, scikit-image), as used in the design. Role B writes only under `routing/` (and `validation/`, which this feature does not touch). The router is one module, `routing/route.py`, built from a pure core and a thin I/O shell. A synthetic data generator in `routing/test_data/make_synthetic.py` lets the router and tests run before real data exists. Tests use only synthetic data or arrays defined in the test code, never `data/processed/`, and contain no validation reference numbers. Every command-line script prints one line per file written (path and size in bytes).

Steps build on each other: dependencies and config, config loading, generator, input loading, cost raster and coordinates, path search, output writing, CLI wiring, then scenario tests.

## Tasks

- [x] 1. Set up dependencies, config file, and router skeleton
  - [x] 1.1 Add test dependencies to `routing/requirements.txt`
    - Install `hypothesis` and `pytest` into `.venv`, then add both with pinned versions in the same `name==version` style as the existing lines
    - This is the only change to that file
    - _Requirements: 9.1_

  - [x] 1.2 Create `routing/config.json` with the shipped parameters
    - Keys: `cost_function`, `slope_limit_deg`, `cost_base`, `cost_coefficient`, `cost_exponent`, `connectivity`, each as `{value, basis}`
    - Values and basis texts exactly as in the design table (limit 20, base 1.0, coefficient 1.0, exponent 2.0, connectivity 8)
    - The slope limit basis contains the JPL URL, "team choice", and "not a human or spacesuit limit"; the cost function basis contains the Minetti URL, "Earth gravity", and "relative cost ranking"
    - Every basis states source, version, and a `YYYY-MM-DD` date
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

  - [x] 1.3 Create `routing/route.py` with core types and config loading
    - Define `RoutingError(message, exit_code)`, frozen dataclasses `CostParams` and `Grid`, and constants `OUT_DIR` and `MAX_BYTES` (52,428,800)
    - Implement `load_config(path)` returning `(CostParams, raw_config)`
    - Validate: file exists and is valid JSON; every key has non-empty `value` and `basis`; basis has a `YYYY-MM-DD` date checked with `datetime.date.fromisoformat`; numeric values are finite, greater than 0, and not bool; `connectivity` is 4 or 8; `cost_function` equals `"quadratic_slope"`
    - Errors raise `RoutingError` with exit code 2 and a message naming the file, the key, and the rejected value
    - No cost constants or defaults in code
    - _Requirements: 1.1, 1.2, 1.6, 1.7, 1.8, 3.6_

- [ ] 2. Test fixtures and config tests
  - [ ] 2.1 Create `routing/tests/conftest.py`
    - Add `routing/` to `sys.path`
    - Shared hypothesis strategies: `slope_grids` (2 to 20 rows and columns; sampled floats in [0, 90], values exactly at the limit, `np.nextafter` above the limit, NaN), `grids`, `endpoints` (including equal pairs), `bad_configs` (mutations of the shipped config)
    - Helpers that write temporary slope, grid, and config files into a fresh temporary directory per example, and a fixture that monkeypatches `OUT_DIR`
    - Tests never reference `data/processed`
    - _Requirements: 8.1_

  - [ ]* 2.2 Write property test and smoke tests for config in `routing/tests/test_config.py`
    - **Property 1: Config validation rejects every invalid config**
    - **Validates: Requirements 1.2, 1.6, 1.7, 3.6**
    - Smoke tests on the shipped `config.json`: values equal the shipped table; bases contain the JPL URL, "team choice", "not a human or spacesuit limit", the Minetti URL, "Earth gravity", "relative cost ranking"
    - Missing and malformed config file tests
    - _Requirements: 1.3, 1.4, 1.5, 1.6_

- [x] 3. Implement the synthetic test data generator
  - [x] 3.1 Create `routing/test_data/make_synthetic.py`
    - Implement `generate(seed, width, height, pixel_size_m, steep_deg) -> (slope, grid_dict)` using `numpy.random.default_rng(seed)` and a Gaussian-filtered noise field scaled into 2 to 15 degrees
    - Plant a flat block (at least 10 cells, values at or below 1.0), a steep block (at least 10 cells, `slope_limit + 10` capped at 90, limit read from `routing/config.json`), and at least one NaN cell
    - Clip finite values to 0 to 90 and cast to float32
    - Grid dict: `pixel_size_m`, `width`, `height`, `top_left`, `crs` containing `SYNTHETIC`, `synthetic: true`, `nodata_value: null`
    - CLI: `--seed` (required integer), `--width`, `--height` (1 to 1024, defaults 64), `--pixel-size` (default 1.0), `--config`
    - Reject a missing or non-integer seed, bad sizes, and sizes whose file would reach 52,428,800 bytes
    - Write `grid.json` with sorted keys and 2-space indent; write both files to temporary names, then `os.replace` both so existing files stay unchanged on failure
    - Write only under `routing/test_data/` and create it if missing
    - Print one line per file written (path and size in bytes)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 9.3_

  - [ ]* 3.2 Write property test for generated data in `routing/tests/test_generator.py`
    - **Property 12: Generated test data is valid and contains the required features**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**

  - [ ]* 3.3 Write property test for generator determinism in `routing/tests/test_generator.py`
    - **Property 13: Generator is deterministic**
    - **Validates: Requirements 7.4**

  - [ ]* 3.4 Write unit tests for the generator CLI in `routing/tests/test_generator.py`
    - One output line per file, missing seed, non-integer seed, unwritable directory leaves earlier files unchanged, oversize request rejected
    - _Requirements: 7.6, 7.7, 7.8_

- [x] 4. Implement input loading
  - [x] 4.1 Add `load_grid` and `load_slope` to `routing/route.py`
    - `load_grid`: file exists, valid JSON, all of `pixel_size_m`, `width`, `height`, `top_left`, `crs` present (message names every missing field), `pixel_size_m` a number greater than 0, `width` and `height` integers greater than 0 (message names field and value)
    - `load_slope`: file exists, valid NumPy array, exactly 2 dimensions (message states actual ndim), shape equals `(height, width)` (message states both shapes)
    - All errors raise `RoutingError` exit code 2 and name the file; nothing is written
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

  - [ ]* 4.2 Write property test for input validation in `routing/tests/test_inputs.py`
    - **Property 3: Malformed inputs are rejected with a message naming the cause**
    - **Validates: Requirements 2.2, 2.4, 2.5, 2.6, 2.8**

  - [ ]* 4.3 Write unit tests for file errors in `routing/tests/test_inputs.py`
    - Missing, unreadable, and malformed slope and grid files; a valid pair loads correctly
    - _Requirements: 2.3, 2.7_

- [x] 5. Implement cost raster and coordinate conversion
  - [x] 5.1 Add `build_cost_raster`, `coord_to_pixel`, and `pixel_to_coord` to `routing/route.py`
    - Cost: float64, same shape; promote slope to float64; `abs_slope <= limit` is traversable with `base + coefficient * (abs_slope / limit) ** exponent`; NaN and values above the limit are `np.inf`
    - `coord_to_pixel` uses `floor` formulas from the design; `pixel_to_coord` returns the pixel centre
    - _Requirements: 1.8, 3.1, 3.2, 3.3, 3.4, 3.5, 3.7, 4.2, 6.3_

  - [ ]* 5.2 Write property test for the cost raster in `routing/tests/test_cost.py`
    - **Property 2: Cost raster follows the configured formula**
    - **Validates: Requirements 1.8, 3.1, 3.2, 3.3, 3.4, 3.7**

  - [ ]* 5.3 Write property test for coordinate conversion in `routing/tests/test_endpoints.py`
    - **Property 4: Coordinate conversion is consistent with the pixel grid**
    - **Validates: Requirements 4.2, 6.3**

- [x] 6. Implement endpoint resolution and path search
  - [x] 6.1 Add `resolve_endpoint`, `find_path`, and `path_cost` to `routing/route.py`
    - `resolve_endpoint`: accept pixel or coordinate form, reject non-finite values (exit 2, names endpoint and value), reject cells outside the grid (exit 1, names start or end)
    - `find_path`: check blocked endpoints first (message names start, end, or both); call `route_through_array(cost, start, end, fully_connected=(connectivity == 8), geometric=True)`; a `ValueError` or infinite cost becomes "no path exists" (exit 1)
    - `path_cost`: sum of `0.5 * (c_i + c_j) * step_length`
    - Identical start and end gives a single-cell path
    - _Requirements: 4.1, 4.5, 4.7, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ]* 6.2 Write property test for path validity in `routing/tests/test_path.py`
    - **Property 5: Returned paths are valid**
    - **Validates: Requirements 3.5, 5.1, 5.6**

  - [ ]* 6.3 Write property test for path optimality in `routing/tests/test_path.py`
    - **Property 6: Returned paths are cost-optimal**
    - Reference Dijkstra (heapq, same step-cost rule) in the test file, grids at most 8 by 8
    - **Validates: Requirements 5.1, 5.4**

  - [ ]* 6.4 Write property test for path cost symmetry in `routing/tests/test_path.py`
    - **Property 7: Path cost is symmetric**
    - **Validates: Requirements 5.7**

  - [ ]* 6.5 Write unit tests for unreachable behavior in `routing/tests/test_path.py`
    - Pin the installed scikit-image behavior when no finite path exists (raise or infinite cost) and confirm it becomes "no path exists"
    - Single-cell route; blocked start, blocked end, both blocked messages
    - _Requirements: 5.2, 5.3, 5.4_

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement GeoJSON route output
  - [ ] 8.1 Add `validate_name`, `get_commit_hash`, `build_feature`, and `write_route` to `routing/route.py`
    - `validate_name`: regex `^[A-Za-z0-9_-]{1,64}$`, error exit 2 naming the rule
    - `get_commit_hash`: `git rev-parse HEAD`, returns `"unknown"` on any failure
    - `build_feature`: one Feature, LineString of pixel-centre coordinates in path order, exactly nine properties (`name`, `start_poi`, `end_poi`, `length_m`, `max_slope_deg`, `slope_threshold_deg`, `data_used`, `cost_function`, `generated_from`); `length_m` and `max_slope_deg` rounded to 2 decimals; `cost_function` text built from loaded config values, 1 to 500 characters; `generated_from` is `commit=<hash>; config=<minified config>`; no validation metric
    - `write_route`: create `OUT_DIR` if missing; write to a temporary file in the same directory, check the size against `MAX_BYTES` before `os.replace`, remove the temporary file on any error; 2-space indent, UTF-8; error messages name the file path
    - _Requirements: 4.3, 4.4, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 6.13, 6.16, 6.17, 9.3, 9.4, 9.7_

  - [ ]* 8.2 Write property test for the route round trip in `routing/tests/test_output.py`
    - **Property 9: Route file round trip**
    - **Validates: Requirements 4.3, 4.4, 6.3, 6.15**

  - [ ]* 8.3 Write property test for route properties in `routing/tests/test_output.py`
    - **Property 10: Route properties match the route**
    - **Validates: Requirements 6.1, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 9.7**

  - [ ]* 8.4 Write unit tests for output edge cases in `routing/tests/test_output.py`
    - Output directory created when absent; git failure gives `unknown` (monkeypatch `subprocess.run`); write failure leaves no partial file (monkeypatch `os.replace`); size limit with `MAX_BYTES` patched small gives non-zero exit and no file
    - _Requirements: 6.13, 6.16, 6.17, 9.4_

- [ ] 9. Wire the router command line
  - [ ] 9.1 Add `main(argv)` and the `__main__` entry to `routing/route.py`
    - argparse: `--name`; mutually exclusive required groups `--start-rc ROW COL` or `--start-en E N`, and `--end-rc` or `--end-en`; `--start-poi`, `--end-poi`; `--slope`, `--grid`, `--config` with defaults resolved against the repository root
    - Order: arguments, name, config, grid, slope, endpoints, cost raster, path, then write
    - Catch `RoutingError`, print `error: <message>` to stderr, return its exit code; invalid arguments exit non-zero (argparse code 2) with usage on stderr and write nothing
    - On success print exactly one line `routing/out/route_<name>.geojson <size_bytes>` and return 0
    - No prompts, no windows, no validation metrics, no comparison routes
    - _Requirements: 2.1, 4.1, 4.6, 4.7, 6.14, 9.1, 9.2, 9.5, 9.6, 9.7_

  - [ ]* 9.2 Write property test for unreachable runs in `routing/tests/test_cli.py`
    - **Property 8: Unreachable runs write nothing**
    - **Validates: Requirements 4.5, 5.3, 5.4, 5.5**

  - [ ]* 9.3 Write property test for route name validation in `routing/tests/test_output.py`
    - **Property 11: Route name validation**
    - **Validates: Requirements 6.1, 6.2**

  - [ ]* 9.4 Write unit tests for CLI behavior in `routing/tests/test_cli.py`
    - Argument defaults, both endpoint forms given, missing endpoint, NaN endpoint, no output on usage error
    - Subprocess run with closed stdin exits 0 and opens no window; one stdout line with path and size
    - _Requirements: 2.1, 4.6, 4.7, 9.2, 9.5, 9.6_

- [ ] 10. Scenario tests on synthetic data
  - [ ]* 10.1 Write scenario tests in `routing/tests/test_scenarios.py`
    - Ridge row with one gap cell: success, path contains the gap cell, no cell above the limit
    - Full-width ridge: Unreachable, no route file
    - NaN on the start cell and NaN on the end cell (two tests): Unreachable, no route file
    - Slope exactly at the limit is traversable and one step above is blocked, on the same grid
    - 5 by 5 hand-computed route with literal expected coordinates (tolerance 1e-9 m) and properties, with `start_poi` and `end_poi` null and set variants
    - Two temporary configs differing only in `slope_limit_deg`: the lower limit gives a longer route or Unreachable, never a shorter one; default config file not modified
    - All arrays at most 100 by 100 cells, or generator output written into `tmp_path`
    - _Requirements: 4.1, 4.4, 6.9, 6.14, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ]* 10.2 Write hygiene tests in `routing/tests/test_scenarios.py`
    - Lint-style test: test sources contain no reference to `data/processed` and no validation reference values
    - Python version is 3.12 or newer (assert sys.version_info >= (3, 12); do not test for equality with 3.12)
    - _Requirements: 8.1, 8.8, 9.1_

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Run `python -m pytest routing/tests -q` and ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties; each runs at least 100 examples and carries the comment `Feature: b-routing, Property <n>: <text>`
- Unit tests validate specific examples and edge cases
- Role B edits only `routing/`; `docs/ai_log/` entries are added separately after each Kiro run
- No task computes or writes validation numbers

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["2.1", "3.1", "4.1"] },
    { "id": 2, "tasks": ["2.2", "3.2", "4.2", "5.1"] },
    { "id": 3, "tasks": ["3.3", "4.3", "5.2", "5.3", "6.1"] },
    { "id": 4, "tasks": ["3.4", "6.2", "8.1"] },
    { "id": 5, "tasks": ["6.3", "8.2", "9.1"] },
    { "id": 6, "tasks": ["6.4", "8.3", "9.2"] },
    { "id": 7, "tasks": ["6.5", "8.4", "9.4", "10.1"] },
    { "id": 8, "tasks": ["9.3", "10.2"] }
  ]
}
```
