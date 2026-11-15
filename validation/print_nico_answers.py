"""Read-only. Print the facts Nico asked for. Writes nothing.

Run: .\\.venv\\Scripts\\python.exe validation\\print_nico_answers.py
All numbers are computed here. No route is compared with anything.
"""
from __future__ import annotations

import collections
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

from fill_params import aeqd_forward, haversine

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "validation" / "data"
PARAMS = ROOT / "validation" / "params.json"
GRID = ROOT / "data" / "processed" / "grid.json"
SLOPE = ROOT / "data" / "processed" / "slope.npy"
R = 3396190.0  # checked against crs_wkt below


def seg_coords(f):
    g = f["geometry"]
    ls = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    return [p for l in ls for p in l]


def main() -> int:
    grid = json.loads(GRID.read_text(encoding="utf-8"))
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    gv = params["grid"]["pixel_size_and_extent"]["values"]
    px = gv["pixel_size_m"]
    xr, yr = gv["x_range_m"], gv["y_range_m"]
    assert (gv["top_left_x_m"], gv["top_left_y_m"], px, gv["width"], gv["height"]) == (
        grid["top_left_x_m"], grid["top_left_y_m"], grid["pixel_size_m"], grid["width"], grid["height"]), "params.json grid values differ from grid.json"
    assert f"{R:.0f}" in grid["crs_wkt"], "radius not found in crs_wkt"
    x0, x1, y0, y1 = xr[0], xr[1], yr[0], yr[1]  # x_min,x_max,y_min,y_max (outer corners)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c_lat, c_lon = math.degrees(cy / R), math.degrees(cx / R)

    def to_xy(lon, lat):
        return R * math.radians(lon), R * math.radians(lat)

    def inside(lon, lat):
        x, y = to_xy(lon, lat)
        return x0 <= x <= x1 and y0 <= y <= y1

    def dist(lon1, lat1, lon2, lat2):
        a = aeqd_forward(lat1, lon1, c_lat, c_lon, R)
        b = aeqd_forward(lat2, lon2, c_lat, c_lon, R)
        return math.hypot(b[0] - a[0], b[1] - a[1])

    # ---------------- 1. PLACES ----------------
    print("=" * 70)
    print("1. best_interp.csv")
    with open(DATA / "best_interp.csv", "r", encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))
    print("frame values and row counts:", dict(collections.Counter(r["frame"] for r in rows)))
    site = [r for r in rows if r["frame"] == "SITE"]
    print(f"\nframe=SITE rows ({len(site)}): site, sol, planetocentric_latitude, longitude")
    for r in site:
        print(f"  site {r['site']:>3}  sol {r['sol']:>3}  lat {r['planetocentric_latitude']}  lon {r['longitude']}")
    sol0 = [r for r in rows if r["sol"] == "0"]
    print(f"\nrows with sol=0 ({len(sol0)}); frames: {dict(collections.Counter(r['frame'] for r in sol0))}")
    for r in sol0:
        print(f"  frame {r['frame']}  site {r['site']}  drive {r['drive']}  sol {r['sol']}  lat {r['planetocentric_latitude']}  lon {r['longitude']}")
    first_site = site[0]
    s_lat, s_lon = float(first_site["planetocentric_latitude"]), float(first_site["longitude"])

    # ---------------- 2. field names ----------------
    print("\n" + "=" * 70)
    print("2. property names")
    trav = json.loads((DATA / "M20_traverse.json").read_text(encoding="utf-8"))
    wpts = json.loads((DATA / "M20_waypoints.json").read_text(encoding="utf-8"))
    for name, fc in (("M20_traverse.json", trav), ("M20_waypoints.json", wpts)):
        cnt = collections.Counter(k for f in fc["features"] for k in f["properties"])
        keys = sorted(cnt)
        print(f"{name}: {len(fc['features'])} features")
        print("  fields:", keys)
        print("  has 'sol':", "sol" in cnt, "| fields containing 'dist_total':", [k for k in keys if "dist_total" in k])
        print("  features lacking sol:", len(fc["features"]) - cnt.get("sol", 0))

    # ---------------- 3. in-grid runs ----------------
    print("\n" + "=" * 70)
    print("3. M20_traverse.json after removing partial/duplicate: runs inside the grid")
    feats = trav["features"]
    cs = [seg_coords(f) for f in feats]
    ps = [f["properties"] for f in feats]
    partial = [i for i in range(len(feats)) if len({(p[0], p[1]) for p in cs[i]}) < 2 or (ps[i].get("length") or 0) == 0]
    duplicate = [i for i in range(1, len(feats)) if cs[i] == cs[i - 1]]
    removed = sorted(set(partial) | set(duplicate))
    print(f"partial {partial}; duplicate {duplicate}; removed (0-based) {removed} ({len(removed)})")
    kept = [i for i in range(len(feats)) if i not in set(removed)]
    sols = [ps[i]["sol"] for i in kept]
    sorted_ok = all(a <= b for a, b in zip(sols, sols[1:]))
    print(f"segments kept {len(kept)}; sol nondecreasing in file order: {sorted_ok}")
    order = kept if sorted_ok else sorted(kept, key=lambda i: (ps[i]["sol"], i))
    print(f"grid extent (outer corners, from params.json): x {x0} to {x1}, y {y0} to {y1}; pixel {px} m")
    site_inside = inside(s_lon, s_lat)
    print(f"PLACES first SITE row inside grid: {site_inside}")

    # Vertex stream: (segment index, sol, lon, lat)
    verts = [(i, ps[i]["sol"], p[0], p[1]) for i in order for p in cs[i]]
    flags = [inside(v[2], v[3]) for v in verts]
    runs, start = [], None
    for k, f in enumerate(flags + [False]):
        if f and start is None:
            start = k
        if not f and start is not None:
            runs.append((start, k - 1))
            start = None
    print(f"vertices {len(verts)}; inside {sum(flags)}; runs inside grid: {len(runs)}")
    print("\n run | start sol | end sol | points (raw) | points (no repeats) | length m (aeqd) | start seg | end seg")
    table = []
    for n, (a, b) in enumerate(runs, 1):
        seq = verts[a:b + 1]
        dedup = [seq[0]] + [q for p_, q in zip(seq, seq[1:]) if (q[2], q[3]) != (p_[2], p_[3])]
        length = sum(dist(p_[2], p_[3], q[2], q[3]) for p_, q in zip(dedup, dedup[1:]))
        table.append((n, seq[0], seq[-1], len(seq), len(dedup), length))
        print(f" {n:>3} | {seq[0][1]:>9} | {seq[-1][1]:>7} | {len(seq):>12} | {len(dedup):>19} | {length:>15.3f} | {seq[0][0]:>9} | {seq[-1][0]:>7}")
    if table:
        first = table[0][1]
        d = dist(s_lon, s_lat, first[2], first[3])
        print(f"\nfirst run starts at lon {first[2]}, lat {first[3]} (sol {first[1]}, segment {first[0]})")
        print(f"distance from first run start to PLACES first SITE row: {d:.6f} m (aeqd), "
              f"{haversine(s_lat, s_lon, first[3], first[2], R):.6f} m (haversine)")
    print(f"landing site (PLACES first SITE row) inside grid: {site_inside}")

    # ---------------- 4. slope, POI, route ----------------
    print("\n" + "=" * 70)
    print("4. slope.npy, POI, routes")
    a = np.load(SLOPE)
    print(f"slope.npy: dtype {a.dtype}, shape {a.shape}")
    print(f"  NaN count: {int(np.isnan(a).sum())}; inf count: {int(np.isinf(a).sum())}")
    nodata_keys = [k for k in grid if "nodata" in k.lower() or "no_data" in k.lower()]
    print(f"  nodata value declared in grid.json: {[(k, grid[k]) for k in nodata_keys] if nodata_keys else 'none (no nodata key)'}")
    fin = a[np.isfinite(a)]
    print(f"  finite min {fin.min():.6g}, max {fin.max():.6g}; values < 0: {int((fin < 0).sum())}; values > 90: {int((fin > 90).sum())}; values > 20: {int((fin > 20).sum())}")
    for sentinel in (-9999.0, -32768.0, -3.4028234663852886e38, 0.0):
        print(f"  count == {sentinel:g}: {int((a == sentinel).sum())}")

    for label, path in (("data/processed/poi.geojson", ROOT / "data" / "processed" / "poi.geojson"),
                        ("web/public/data/poi.geojson", ROOT / "web" / "public" / "data" / "poi.geojson")):
        pois = json.loads(path.read_text(encoding="utf-8"))["features"]
        ds = sorted((dist(s_lon, s_lat, f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][1]), f["properties"].get("id")) for f in pois)
        within = [x for x in ds if x[0] < px]
        print(f"{label}: {len(pois)} points; nearest to PLACES SITE row: {ds[0][1]} at {ds[0][0]:.3f} m; "
              f"points closer than 1 pixel ({px} m): {[x[1] for x in within] if within else 'none'}")

    skip = {".venv", "node_modules", ".git", "__pycache__"}
    route_files = sorted(p for p in ROOT.rglob("*.geojson") if not (skip & set(p.relative_to(ROOT).parts)) and "poi" not in p.name)
    print(f"route geojson files found: {[str(p.relative_to(ROOT)) for p in route_files]}")
    best = None
    for p in route_files:
        gj = json.loads(p.read_text(encoding="utf-8"))
        geom = gj["geometry"] if gj.get("type") == "Feature" else gj["features"][0]["geometry"]
        first_pt = (geom["coordinates"][0] if geom["type"] == "LineString" else geom["coordinates"][0][0])
        props = gj.get("properties", {}) if gj.get("type") == "Feature" else gj["features"][0].get("properties", {})
        geographic = abs(first_pt[0]) <= 360 and abs(first_pt[1]) <= 90
        print(f"  {p.relative_to(ROOT)}: first coordinate {first_pt}; geographic lon/lat range: {geographic}")
        print(f"    properties: cost_function={props.get('cost_function')!r}; generated_from={props.get('generated_from')!r}")
        if geographic:
            d = dist(s_lon, s_lat, first_pt[0], first_pt[1])
            print(f"    distance from route start to PLACES first SITE row: {d:.3f} m")
            best = min(best, (d, str(p.relative_to(ROOT)))) if best else (d, str(p.relative_to(ROOT)))
        else:
            print("    first coordinate is not in longitude/latitude range; no distance computed")
    if best:
        print(f"nearest route start: {best[1]} at {best[0]:.3f} m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
