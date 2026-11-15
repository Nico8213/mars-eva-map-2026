"""Read-only: print the CRS string and planet radius stored in data/processed/grid.json.

Nothing is hard-coded. The radius is parsed from the SPHEROID entry of the CRS WKT,
because grid.json has no separate radius field.
"""
import json
import re
from pathlib import Path

GRID = Path(__file__).resolve().parent.parent / "data" / "processed" / "grid.json"

with GRID.open("r", encoding="utf-8") as f:
    grid = json.load(f)

crs = grid["crs_wkt"]
m = re.search(r'SPHEROID\["([^"]*)",\s*([^,\]]+),\s*([^,\]]+)', crs)
if m is None:
    raise SystemExit("No SPHEROID entry found in crs_wkt")

print("file:", GRID)
print("crs_wkt:", crs)
print("spheroid name:", m.group(1))
print("semi-major axis (m):", m.group(2))
print("inverse flattening:", m.group(3))
