# Design: a-poi

Flow: load grid.json and layers.json, then read the CSV. Validate each row (source, integer pixels, pixel bounds). Compute the pixel-centre easting/northing from grid.json. Reproject all points in one `rasterio.warp.transform` call, using the CRS built from `crs_wkt`. Check each point against the layers.json extent. Write the GeoJSON (UTF-8, 2-space indent) and print the summary.

Notes:
- `layers.json` extent is taken from the first layer. All layers share the same extent.
- Every error prints a message naming the row id and calls `sys.exit(1)`. Nothing is written when validation fails.
- `docs/INTERFACES.md` describes poi coordinates as easting/northing with the CRS undecided. This spec follows the user's request for lon/lat degrees. INTERFACES.md should be updated separately.
