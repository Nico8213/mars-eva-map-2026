"""Read-only. PLACES path inside the grid, and a look at routing/out. Writes nothing.

Path = first SITE row, then all frame == ROVER rows by ascending sol (ties keep
file order). Points use planetocentric_latitude and longitude on the sphere
R = 3396190 m. Grid extent comes from validation/params.json. No comparison
with any route is made.
Run: .\\.venv\\Scripts\\python.exe validation\\print_places_segments.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

from fill_params import aeqd_forward

ROOT = Path(__file__).resolve().parents[1]
R = 3396190.0


def main() -> int:
    params = json.loads((ROOT / "validation" / "params.json").read_text(encoding="utf-8"))
    grid = json.loads((ROOT / "data" / "processed" / "grid.json").read_text(encoding="utf-8"))
    assert f"{R:.0f}" in grid["crs_wkt"], "radius not found in crs_wkt"
    gv = params["grid"]["pixel_size_and_extent"]["values"]
    x0, x1 = gv["x_range_m"]
    y0, y1 = gv["y_range_m"]
    c_lat, c_lon = math.degrees((y0 + y1) / 2 / R), math.degrees((x0 + x1) / 2 / R)
    print(f"grid extent from params.json: x {x0} to {x1}, y {y0} to {y1}; sphere R = {R:.0f} m; aeqd centre lat {c_lat:.6f} lon {c_lon:.6f}")

    def inside(lon, lat):
        x, y = R * math.radians(lon), R * math.radians(lat)
        return x0 <= x <= x1 and y0 <= y <= y1

    def d(a, b):
        p = aeqd_forward(a["lat"], a["lon"], c_lat, c_lon, R)
        q = aeqd_forward(b["lat"], b["lon"], c_lat, c_lon, R)
        return math.hypot(q[0] - p[0], q[1] - p[1])

    with open(ROOT / "validation" / "data" / "best_interp.csv", "r", encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))

    def pt(r, label):
        return {"lat": float(r["planetocentric_latitude"]), "lon": float(r["longitude"]), "sol": r["sol"], "label": label}

    site = next(r for r in rows if r["frame"] == "SITE")
    rover = [r for r in rows if r["frame"] == "ROVER"]
    rover_sorted = sorted(rover, key=lambda r: int(r["sol"]))  # stable: ties keep file order
    path = [pt(site, "SITE")] + [pt(r, "ROVER") for r in rover_sorted]
    print(f"\na. path points: {len(path)} (1 SITE + {len(rover_sorted)} ROVER)")
    flags = [inside(p["lon"], p["lat"]) for p in path]
    print(f"   points inside grid: {sum(flags)}; landing site (first path point) inside grid: {flags[0]}")

    runs, start = [], None
    for k, f in enumerate(flags + [False]):
        if f and start is None:
            start = k
        if not f and start is not None:
            runs.append((start, k - 1))
            start = None
    print(f"   runs inside the grid: {len(runs)}")
    print("   run | start index | start sol | end sol | points | distinct points | length m (aeqd)")
    for n, (a, b) in enumerate(runs, 1):
        seq = path[a:b + 1]
        distinct = len({(p["lat"], p["lon"]) for p in seq})
        length = sum(d(p, q) for p, q in zip(seq, seq[1:]))
        s0 = seq[0]["sol"] if seq[0]["label"] == "ROVER" else "n/a"
        s1 = seq[-1]["sol"] if seq[-1]["label"] == "ROVER" else "n/a"
        print(f"   {n:>3} | {a:>11} | {s0:>9} | {s1:>7} | {len(seq):>6} | {distinct:>15} | {length:>15.3f}")
    print(f"   first run starts at the landing site (path index 0): {bool(runs) and runs[0][0] == 0}")

    print("\nb. ROVER rows with the smallest sol (as in the file): frame, site, drive, sol, planetocentric_latitude, longitude")
    smallest = sorted(range(len(rover)), key=lambda i: int(rover[i]["sol"]))[:10]
    for i in smallest:
        r = rover[i]
        print(f"   {r['frame']}  site {r['site']}  drive {r['drive']}  sol {r['sol']}  lat {r['planetocentric_latitude']}  lon {r['longitude']}")

    print("\nc. routing/out/ geojson files")
    out = ROOT / "routing" / "out"
    files = sorted(out.glob("*.geojson")) if out.is_dir() else []
    print(f"   found: {[f.name for f in files] if files else 'none'}")
    for f in files:
        gj = json.loads(f.read_text(encoding="utf-8"))
        feat = gj["features"][0] if gj.get("type") == "FeatureCollection" else gj
        geom = feat["geometry"]
        first = geom["coordinates"][0] if geom["type"] == "LineString" else geom["coordinates"][0][0]
        props = feat.get("properties", {})
        crs = gj.get("crs") or feat.get("crs")
        notes = {k: v for k, v in props.items() if any(w in k.lower() for w in ("crs", "unit", "coord", "projection"))}
        if crs:
            verdict = f"crs field: {crs}"
        elif notes:
            verdict = f"properties: {notes}"
        else:
            verdict = "cannot tell (no crs field and no coordinate note in properties)"
        print(f"   {f.name}: first coordinate {first}; {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
