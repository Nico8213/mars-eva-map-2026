# Tasks: b-routing-exclude

- [x] 1. Config
  - [x] 1.1 Add `cost_inputs` (`["slope"]`, basis with source and date) to `routing/config.json`
  - _Requirements: R1.3_

- [x] 2. Code in `routing/route.py`
  - [x] 2.1 `load_layer_ids` and `load_cost_inputs`
  - [x] 2.2 `slope_removed` option in `build_cost_raster`
  - [x] 2.3 `data_used`, `exclude` options in `build_feature` and `_cost_function_text`
  - [x] 2.4 `--exclude`, `--layers` arguments and wiring in `main`
  - _Requirements: R1 to R5_

- [x] 3. Verify
  - [x] 3.1 Fake grid: normal run, `--exclude slope`, `--exclude hillshade`, invalid layer
  - [x] 3.2 Real grid: same runs
  - [x] 3.3 Check properties against INTERFACES.md and that `validation/params.json` is unchanged
  - [x] 3.4 Run the existing pytest suite
  - _Requirements: R1 to R5_

- [x] 4. Housekeeping
  - [x] 4.1 Update `routing/README.md`
  - [x] 4.2 Add one line to `docs/ai_log/B-austin.md`

