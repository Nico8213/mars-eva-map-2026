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
- If a point of interest lies on a blocked cell, or no path exists, the route is reported as "unreachable". No fallback endpoint is invented.
- Path search: `skimage.graph.route_through_array` with `fully_connected=True` and `geometric=True`.

## 4. Validation
- Validation route: start at the first point of the Perseverance traverse (the landing site); end at the last traverse point that lies inside the extent of `grid.json`.
- Metric(s): mean distance and maximum distance, in meters, between our validation route and the Perseverance traverse. Both lines are resampled at a fixed spacing of one grid pixel (taken from `grid.json`); for each sample on our route, the distance to the nearest sample on the traverse is computed. Metrics are computed by code, never typed by hand.
- Parameters (locked before running; committed in `validation/params.json` before the first validation run and not changed afterwards):
  - slope limit: 20 degrees
  - cost formula: `1 + (slope / limit)^2`
  - connectivity: `fully_connected=True`, `geometric=True`
  - pixel size and grid extent: read from `grid.json`
  - resampling spacing: one grid pixel
  - traverse file: the exact file and download date, recorded in the report
- Comparison segment(s): the whole Perseverance traverse, clipped to the extent of `grid.json`. Parts of the traverse outside the grid are not compared.
- Traverse data source: https://science.nasa.gov/mission/mars-2020-perseverance/location-map/ . A direct GeoJSON link was reported by a forum user (https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_traverse.json); it must be checked before use. VN provides the final source link, and the small file goes in `validation/data/`.
- Caveat: the rover traverse is not the optimal route for a person on foot. The comparison is a sanity check, not ground truth. Results are reported as they are, good or bad.

## 5. Comparison routes (F10)
- Data layer removed in each comparison: one comparison route per layer listed in `data/processed/layers/layers.json`, each with that single layer removed from the cost inputs. Output file name: `route_<name>_no_<layer>.geojson`.
- Only layers that `routing/config.json` declares as cost inputs can change a route. Layers that are not cost inputs are listed in the report as "no effect on routing".