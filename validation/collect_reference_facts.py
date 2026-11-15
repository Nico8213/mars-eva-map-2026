"""Read-only. Collect the facts that params.json needs, all computed from files.

Reads: data/processed/grid.json, data/processed/layers/layers.json,
data/processed/sources.md, docs/INTERFACES.md (text only),
validation/data/{best_interp.csv, M20_traverse.json, M20_waypoints.json,
SNAPSHOT.md}. Writes nothing. Importable: collect() returns a dict.
Run: .\\.venv\\Scripts\\python.exe validation\\collect_reference_facts.py
Exits with code 2 and a STOP message if the grid corner convention cannot be
established from the files.
"""
from __future__ import annotations

import collections
import csv
import datetime
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "validation" / "data"
GRID = ROOT / "data" / "processed" / "grid.json"
LAYERS = ROOT / "data" / "processed" / "layers" / "layers.json"
SOURCES = ROOT / "data" / "processed" / "sources.md"
INTERFACES = ROOT / "docs" / "INTERFACES.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest().upper()


def mtime(path: Path) -> str:
    return datetime.datetime.fromtimestamp(path.stat().st_mtime).astimezone().strftime("%Y-%m-%d %H:%M:%S UTC%z")


def stop(msg: str):
    print("STOP:", msg)
    raise SystemExit(2)


def grid_convention(grid: dict) -> dict:
    """Decide whether top_left_x_m / top_left_y_m are the outer corner of the top-left pixel or its centre."""
    x0, y0 = grid["top_left_x_m"], grid["top_left_y_m"]
    px, w, h = grid["pixel_size_m"], grid["width"], grid["height"]
    x1, y1 = x0 + w * px, y0 - h * px
    ev = {}

    # (a) sources.md: crop extent in projected metres.
    text = SOURCES.read_text(encoding="utf-8")
    m = re.search(r"projected x\s+(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)\s*m,\s*y\s+(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)", text)
    if not m:
        stop("crop extent not found in data/processed/sources.md; cannot decide corner or centre.")
    sx0, sx1, sy0, sy1 = map(float, m.groups())
    ev["sources_md_extent_m"] = {"x_min": sx0, "x_max": sx1, "y_min": sy0, "y_max": sy1}
    ev["sources_md_matches_outer_corner"] = (sx0, sx1, sy0, sy1) == (x0, x1, y1, y0)
    # If top_left were the pixel centre, the outer edges would be half a pixel further out.
    ev["sources_md_matches_centre_alternative"] = (sx0, sx1, sy0, sy1) == (x0 - px / 2, x1 - px / 2, y1 + px / 2, y0 + px / 2)

    # (b) layers.json: image extents in degrees (the displayed image bounds), inverse equirectangular on the sphere.
    wkt = grid["crs_wkt"]
    r = float(re.search(r'SPHEROID\["[^"]*",\s*([0-9.eE+-]+)', wkt).group(1))
    lay = json.loads(LAYERS.read_text(encoding="utf-8"))
    slope_layer = next(l for l in lay if l["name"] == "Slope")["extent"]

    def inv(x, y):
        return math.degrees(y / r), math.degrees(x / r)

    nlat, wlon = inv(x0, y0)
    slat, elon = inv(x1, y1)
    diffs = {"west": slope_layer["west"] - wlon, "east": slope_layer["east"] - elon,
             "north": slope_layer["north"] - nlat, "south": slope_layer["south"] - slat}
    ev["layers_json_slope_extent_minus_outer_corner_deg"] = diffs
    ev["layers_json_matches_outer_corner"] = all(abs(v) < 1e-9 for v in diffs.values())
    half = math.degrees(px / 2 / r)
    ev["half_pixel_in_degrees_for_scale"] = half

    # (c) text statements.
    ev["grid_json_coordinate_notes"] = grid.get("coordinate_notes", "")[:80]
    iface = [l.strip() for l in INTERFACES.read_text(encoding="utf-8").splitlines() if "top-left pixel corner" in l or "top-left corner of pixel" in l]
    ev["interfaces_md_lines"] = iface

    if not (ev["sources_md_matches_outer_corner"] and ev["layers_json_matches_outer_corner"]) or ev["sources_md_matches_centre_alternative"]:
        stop("the files do not agree that top_left_x_m / top_left_y_m is the outer corner. Not guessing; tell Nico. Evidence: " + json.dumps(ev))
    return {
        "conclusion": "outer corner of the top-left pixel",
        "evidence": ev,
        "x_range_m": [x0, x1], "y_range_m": [y1, y0],
        "cell_centre_formula": "x_centre = top_left_x_m + (col + 0.5) * pixel_size_m ; y_centre = top_left_y_m - (row + 0.5) * pixel_size_m",
        "half_pixel_m": px / 2,
        "max_end_point_offset_px": math.sqrt(2) / 2,
        "max_end_point_offset_m": math.sqrt(2) / 2 * px,
    }


def places_facts() -> dict:
    p = DATA / "best_interp.csv"
    with open(p, "r", encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))
        header = list(rows[0].keys())
    frames = collections.Counter(r["frame"] for r in rows)
    keys = [(int(r["site"]), 0 if r["frame"] == "SITE" else 1, int(r["drive"]) if r["frame"] != "SITE" else -1) for r in rows]
    order_ok = all(a <= b for a, b in zip(keys, keys[1:]))
    rover_sols = [int(r["sol"]) for r in rows if r["frame"] == "ROVER"]
    sol_ok = all(a <= b for a, b in zip(rover_sols, rover_sols[1:]))
    site_rows = [r for r in rows if r["frame"] == "SITE"]
    n_lines = sum(1 for _ in open(p, "r", encoding="utf-8"))
    return {
        "file": "validation/data/best_interp.csv",
        "bytes": p.stat().st_size,
        "lines_including_header": n_lines,
        "data_rows": len(rows),
        "sha256": sha256(p),
        "file_mtime": mtime(p),
        "columns": header,
        "columns_used": ["planetocentric_latitude", "longitude"],
        "frame_counts": dict(frames),
        "pose_values": sorted({r["pose"] for r in rows}),
        "sites_with_SITE_row": len(site_rows),
        "file_order_nondecreasing_by_site_then_drive": order_ok,
        "rover_sol_nondecreasing_in_file_order": sol_ok,
        "rover_sol_min": min(rover_sols), "rover_sol_max": max(rover_sols),
        "site_row_sol_values": sorted({r["sol"] for r in site_rows}),
    }


def segment_facts() -> dict:
    trav = json.loads((DATA / "M20_traverse.json").read_text(encoding="utf-8"))
    feats = trav["features"]

    def coords(f):
        g = f["geometry"]
        ls = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        return [p for l in ls for p in l]

    cs = [coords(f) for f in feats]
    ps = [f["properties"] for f in feats]
    partial = [i for i in range(len(feats)) if len({(p[0], p[1]) for p in cs[i]}) < 2 or (ps[i].get("length") or 0) == 0]
    duplicate = [i for i in range(1, len(feats)) if cs[i] == cs[i - 1]]
    union = sorted(set(partial) | set(duplicate))
    return {"index_base": 0, "segments": len(feats), "partial": partial, "duplicate": duplicate, "union": union, "union_count": len(union)}


def collect() -> dict:
    grid = json.loads(GRID.read_text(encoding="utf-8"))
    conv = grid_convention(grid)
    text = SOURCES.read_text(encoding="utf-8")
    prod = re.search(r"Official product name:\s*(\S+)", text)
    local = re.search(r"Local file:\s*(\S+)", text)
    return {
        "grid": {"top_left_x_m": grid["top_left_x_m"], "top_left_y_m": grid["top_left_y_m"], "pixel_size_m": grid["pixel_size_m"],
                 "width": grid["width"], "height": grid["height"], "convention": conv,
                 "source_product": grid.get("source_product"), "version": grid.get("version"), "doi": grid.get("doi"),
                 "official_product_name_from_sources_md": prod.group(1) if prod else None,
                 "local_file_from_sources_md": local.group(1) if local else None},
        "places": places_facts(),
        "segments": segment_facts(),
        "mmgis_files": {
            "M20_traverse.json": {"sha256": sha256(DATA / "M20_traverse.json"), "bytes": (DATA / "M20_traverse.json").stat().st_size, "mtime": mtime(DATA / "M20_traverse.json")},
            "M20_waypoints.json": {"sha256": sha256(DATA / "M20_waypoints.json"), "bytes": (DATA / "M20_waypoints.json").stat().st_size, "mtime": mtime(DATA / "M20_waypoints.json")},
        },
    }


def main() -> int:
    f = collect()
    g = f["grid"]
    print("== grid corner convention ==")
    print("conclusion:", g["convention"]["conclusion"])
    print(json.dumps(g["convention"]["evidence"], indent=1))
    print("max end-point offset: %.5f px = %.5f m" % (g["convention"]["max_end_point_offset_px"], g["convention"]["max_end_point_offset_m"]))
    print("== PLACES best_interp.csv ==")
    print(json.dumps(f["places"], indent=1))
    print("== partial / duplicate (0-based) ==")
    print(json.dumps(f["segments"]))
    print("== MMGIS files ==")
    print(json.dumps(f["mmgis_files"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
