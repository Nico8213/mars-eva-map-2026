# Requirements: b-routing-exclude

## Introduction

This feature adds a `--exclude <layer>` switch to `routing/route.py` (spec `b-routing`). It produces the comparison routes of F10: the same route as the normal run, with one data layer removed from the cost calculation. Source of the rule: `docs/research/nico-routing-spec.md`, section 5. Output format: `docs/INTERFACES.md`, section "routing/out/route_<name>.geojson".

Owner: B (`routing/`). Files outside `routing/` are read only. `validation/params.json` is not changed.

## Glossary

- Layer: an entry of `data/processed/layers/layers.json`. Its id is the layer `name` in lower case (for example `Slope` gives `slope`).
- Cost input: a layer that `routing/config.json` lists under `cost_inputs`. Only a cost input can change a route (spec section 5).
- Comparison route: a route computed with one layer excluded.

## Requirements

### R1: Which layers can be excluded

**User story:** As a reviewer, I want to remove one layer and see whether the route changes, without the tool inventing layers.

Acceptance criteria:
1. THE valid values of `--exclude` SHALL be exactly the layer ids found in `data/processed/layers/layers.json`. No other value is accepted and no layer is added in code.
2. IF the value is not a layer id, THEN THE script SHALL exit with code 2 and print the rejected value and the valid ids to stderr. No file is written.
3. THE script SHALL read the list of cost inputs from a new `cost_inputs` entry in `routing/config.json` (`value` and `basis` with a date, like every other entry). The value is `["slope"]`.
4. IF `--exclude` is used and `cost_inputs` is missing or invalid, THEN THE script SHALL exit with code 2 and name the file and key.
5. Without `--exclude`, the behaviour and output of the script SHALL stay exactly as before, and `cost_inputs` is not required.

### R2: Effect on the cost

Acceptance criteria:
1. WHEN the excluded layer is a cost input, THE script SHALL compute the cost raster without it. For `slope` this means every cell costs `cost_base`, and no cell is blocked by slope or by missing slope data, because the layer that carries those values is removed.
2. WHEN the excluded layer is not a cost input, THE script SHALL compute the same cost raster as the normal run. The route is the same as without `--exclude`. The script SHALL print one line to stderr: the layer has "no effect on routing".
3. The path search is unchanged (`fully_connected` and `geometric` from the config).

### R3: Output file

Acceptance criteria:
1. THE script SHALL write `routing/out/route_<name>_no_<layer>.geojson`, where `<name>` is the value of `--name` and `<layer>` is the layer id. The file is written with the same atomic write and 50 MB limit as the normal route file.
2. THE combined name `<name>_no_<layer>` SHALL pass the same name check as `--name` (`^[A-Za-z0-9_-]{1,64}$`).
3. THE script SHALL NOT overwrite or change `route_<name>.geojson`.

### R4: Properties (INTERFACES.md)

Acceptance criteria:
1. THE Feature SHALL contain all properties of the route file: `name`, `start_poi`, `end_poi`, `length_m`, `max_slope_deg`, `slope_threshold_deg`, `data_used`, `cost_function`, `generated_from`.
2. `name` SHALL equal `<name>_no_<layer>`, so it matches the file name.
3. `length_m` SHALL come from the same function as in the normal run (length of the output polyline, metres).
4. `max_slope_deg` SHALL be the largest slope at the route cells, read from `slope.npy` even when slope is excluded, ignoring invalid cells. IF no route cell has a valid slope, THEN THE script SHALL exit with code 2.
5. `data_used` SHALL list the cost-input layer ids that affected the path: the cost inputs minus the excluded layer. For the shipped config this is `["slope"]` when `hillshade` or `ctx` is excluded, and `[]` when `slope` is excluded.
6. `cost_function` SHALL say that the layer was excluded, and for `slope` that every cell costs `cost_base`. `generated_from` SHALL also record the excluded layer.

### R5: Output line and environment

Acceptance criteria:
1. At the end, THE script SHALL print one line with the output path relative to the repository root and the size in bytes.
2. The existing exit codes stay: 0 success, 1 unreachable, 2 invalid input.
3. Only the Python standard library, numpy and scikit-image are used. All text is in English.

## Out of scope

- Running all comparison routes in one command, or choosing start and end points.
- Excluding more than one layer in one run.
- Changing `docs/INTERFACES.md`, `validation/params.json`, `layers.json` or the web cockpit.
- Adding tests (not requested). The feature is checked by runs on the fake and the real grid.

## Assumptions to confirm

- Spec section 5 says only layers that `routing/config.json` declares as cost inputs can change a route, but the config has no such entry. Adding `cost_inputs: ["slope"]` is derived from the shipped cost function, which uses only slope. Please confirm.
- `layers.json` lists `Slope`, `Hillshade` and `CTX`. So `hillshade` and `ctx` are valid values with no effect on the route.
- With `slope` excluded, cost is uniform (`cost_base`) and nothing is blocked. The spec does not define this case.
- `slope_threshold_deg` keeps the config value because INTERFACES.md requires a number, although the threshold is not applied when slope is excluded. `cost_function` states this.
