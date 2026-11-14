# Design: b-routing-exclude

## Overview

All changes are in `routing/route.py` and `routing/config.json`, plus one README note. The normal path (no `--exclude`) is not changed.

## Flow with `--exclude L`

1. Parse arguments. New: `--exclude L`, `--layers PATH` (default `data/processed/layers/layers.json`).
2. `load_layer_ids(layers_path)` returns the lower-case layer names. `L` must be one of them (R1.1, R1.2).
3. `load_cost_inputs(raw_config, config_path)` reads `cost_inputs.value` (list of non-empty strings, each a known layer id) (R1.3, R1.4).
4. `out_name = f"{name}_no_{L}"`, checked with `validate_name`.
5. Cost raster: `build_cost_raster(slope, params, nodata, use_slope=("slope" not in remaining_inputs))`.
   - Slope still a cost input: normal raster (R2.2).
   - Slope excluded: raster filled with `cost_base`, no `np.inf` (R2.1).
6. `find_path` and `build_feature` as before, with `name=out_name`, `data_used=remaining_inputs`, a changed `cost_function` text and an extra `exclude` note in `generated_from`.
7. `write_route(feature, out_name)` writes `route_<name>_no_<L>.geojson`; the final line is printed as before.

## Changes

| Place | Change |
|---|---|
| `routing/config.json` | New entry `cost_inputs` = `["slope"]` with basis and date. Not in `_REQUIRED_KEYS`, so old runs are unaffected. |
| `build_cost_raster` | New keyword `slope_removed: bool = False`. When true, return `np.full(shape, cost_base)`. |
| `build_feature` | New keywords `data_used`, `exclude`. `max_slope_deg` ignores invalid cells (same result for normal routes, whose cells are all valid). Default values keep current output. |
| `_cost_function_text` | New optional `exclude` argument that adds the exclusion statement. |
| `main` | Wiring above. |
| `routing/README.md` | Document `--exclude`, `--layers`, and remove the "not done" line. |

## Decisions

| Decision | Reason |
|---|---|
| Layer ids come only from `layers.json` | Spec section 5 lists them there; R1 forbids invented layers. |
| `cost_inputs` in config, not in code | Spec section 5 says the config declares the cost inputs. |
| Non-cost layer: write the file anyway, same route | Spec section 5 asks for one file per layer and a "no effect" statement. |
| Uniform cost when slope is removed | The only slope-based cost term and the blocking both come from slope; removing the layer removes both. Documented as an assumption. |

## Error handling

Exit 2: unknown layer, unreadable or malformed `layers.json`, bad `cost_inputs`, bad combined name, no valid slope on the route. Exit 1: unreachable (cannot happen with uniform cost unless an endpoint is outside the grid).

## Verification

Run the CLI on the fake grid (`routing/test_data`) and the real grid (`data/processed`) with `--exclude slope`, `--exclude hillshade`, and an invalid value. Compare against the normal route. Run the existing pytest suite to check that nothing else changed.
