# Requirements: a-poi

Script `pipeline/step4_poi.py` converts `pipeline/poi_manual.csv` to `data/processed/poi.geojson`.

## Inputs
- `pipeline/poi_manual.csv`: id, name, type, pixel_x, pixel_y, source, evidence
- `data/processed/grid.json`: top_left_x_m, top_left_y_m, pixel_size_m, width, height, crs_wkt
- `data/processed/layers/layers.json`: extent (west, east, south, north)

## Requirements
1. REQ-01: Output is a GeoJSON FeatureCollection. Each feature is a Point with coordinates `[longitude, latitude]` in degrees.
2. REQ-02: Pixel centre to projected coordinates, using only values from `grid.json`:
   `easting = top_left_x_m + (pixel_x + 0.5) * pixel_size_m`,
   `northing = top_left_y_m - (pixel_y + 0.5) * pixel_size_m`.
3. REQ-03: Projected to lon/lat the same way as `step3_layers.py`: `rasterio.warp.transform` from the grid CRS (`crs_wkt`) to `EPSG:49900`, falling back to `+proj=longlat +a=3396190 +b=3376200 +no_defs`.
4. REQ-04: Feature properties are `id`, `name`, `type`, `source`, `evidence`. `source` must be `CRISM` or `optical`; any other value prints an error and exits non-zero.
5. REQ-05: `0 <= pixel_x <= width-1` and `0 <= pixel_y <= height-1`, otherwise error and exit non-zero.
6. REQ-06: Each point's lon/lat must lie inside the `layers.json` extent, otherwise error and exit non-zero.
7. REQ-07: The script prints each point's id and lon/lat, then the output path and size in bytes.
8. REQ-08: No invented numbers or names. `config.json`, `grid.json`, `layers.json` and existing scripts are not modified.
