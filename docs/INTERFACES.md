# File formats (starter version, Daniel completes it)
| File | Written by | Read by | Content |
|---|---|---|---|
| data/processed/grid.json | A | B, C | Source product name and version, pixel size (m), width, height, top-left coordinate, coordinate notes |
| data/processed/slope.npy | A | B | 2D array, degrees, same size as grid.json |
| data/processed/layers/*.png and layers.json | A | C | One semi-transparent PNG per layer; layers.json lists name, file, extent and data card id |
| data/processed/poi.geojson | A | B, C | Points of interest: id, name, type, position, source |
| data/processed/data_cards.json | A | C | One data card per layer: source, version, date, resolution, license, known issues |
| routing/out/route_<name>.geojson | B | C | Route; properties: length, max slope, data used |
| validation/out/report.json | B | C, D | Validation metrics (computed by code), parameters, comparison segments |
