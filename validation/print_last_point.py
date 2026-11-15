"""Read-only. Last point of the first in-grid run of the PLACES path. Writes nothing.

Path = first SITE row, then all frame == ROVER rows by ascending sol (ties keep
file order). Grid geometry from validation/params.json (outer-corner
convention, cell centre = corner + (index + 0.5) * pixel). No comparison with
any route.
Run: .\\.venv\\Scripts\\python.exe validation\\print_last_point.py
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
R = 3396190.0
LIMIT = 20.0


def main() -> int:
    params = json.loads((ROOT / "validation" / "params.json").read_text(encoding="utf-8"))
    gv = params["grid"]["pixel_size_and_extent"]["values"]
    tlx, tly, px, W, H = gv["top_left_x_m"], gv["top_left_y_m"], gv["pixel_size_m"], gv["width"], gv["height"]
    x0, x1 = gv["x_range_m"]
    y0, y1 = gv["y_range_m"]
    lines = (ROOT / "validation" / "data" / "best_interp.csv").read_text(encoding="utf-8").splitlines()
    with open(ROOT / "validation" / "data" / "best_interp.csv", "r", encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))

    # ---- 1 ----
    print("1. ROVER rows with drive == 0")
    z = [(k, r) for k, r in enumerate(rows) if r["frame"] == "ROVER" and r["drive"] == "0"]
    print(f"   count: {len(z)}")
    for k, r in z:
        print(f"   file line {k + 2}: {lines[k + 1]}")
    print("   first 3 SITE rows: frame, site, drive, sol")
    for r in [r for r in rows if r["frame"] == "SITE"][:3]:
        print(f"   {r['frame']}, {r['site']}, {r['drive']}, {r['sol']}")
    note = ROOT / "docs" / "research" / "vn-perseverance-traverse.md"
    if note.exists():
        for n, l in enumerate(note.read_text(encoding="utf-8").splitlines(), 1):
            if "ROVER,n,0" in l:
                m = re.search(r"\(1\) Release notes:.*?\(2\)", l)
                print(f"   release-notes wording in {note.name} line {n}: {(m.group(0) if m else l)[:300]}")

    # ---- path ----
    site_k = next(k for k, r in enumerate(rows) if r["frame"] == "SITE")
    rover = [k for k, r in enumerate(rows) if r["frame"] == "ROVER"]
    order = [site_k] + sorted(rover, key=lambda k: int(rows[k]["sol"]))  # stable: ties keep file order
    lat = [float(rows[k]["planetocentric_latitude"]) for k in order]
    lon = [float(rows[k]["longitude"]) for k in order]

    def inside(i):
        x, y = R * math.radians(lon[i]), R * math.radians(lat[i])
        return x0 <= x <= x1 and y0 <= y <= y1

    flags = [inside(i) for i in range(len(order))]
    assert flags[0], "landing site not inside the grid"
    end = 0
    while end + 1 < len(order) and flags[end + 1]:
        end += 1
    print(f"\n2. first in-grid run: path index 0 to {end} ({end + 1} points)")
    k = order[end]
    r = rows[k]
    x, y = R * math.radians(lon[end]), R * math.radians(lat[end])
    col, row = int(math.floor((x - tlx) / px)), int(math.floor((tly - y) / px))
    clamped = col == W or row == H
    col, row = min(col, W - 1), min(row, H - 1)
    cx, cy = tlx + (col + 0.5) * px, tly - (row + 0.5) * px
    a = np.load(ROOT / "data" / "processed" / "slope.npy", mmap_mode="r")
    s = float(a[row, col])
    blocked = bool(np.isnan(s) or s > LIMIT)
    sol_txt = r["sol"] if r["frame"] == "ROVER" else "n/a"
    print(f"   path index {end} (file line {k + 2})")
    print(f"   frame {r['frame']}, site {r['site']}, drive {r['drive']}, sol {sol_txt}")
    print(f"   planetocentric_latitude {r['planetocentric_latitude']}, longitude {r['longitude']}")
    print(f"   projected x {x:.3f}, y {y:.3f}")
    print(f"   grid row {row}, col {col}" + (" (point is on the max edge; clamped to the last row/col)" if clamped else ""))
    print(f"   cell centre x {cx}, y {cy}; offset of the point from the cell centre: dx {x - cx:.3f} m, dy {y - cy:.3f} m, distance {math.hypot(x - cx, y - cy):.3f} m")
    print(f"   slope at that cell: {s:.4f} deg; blocked (>{LIMIT:g} or NaN): {blocked}")
    nxt = end + 1
    if nxt < len(order):
        print(f"   next path point (index {nxt}) is outside the grid: sol {rows[order[nxt]]['sol']}, file line {order[nxt] + 2}")

    # ---- 3 ----
    last_sol = int(r["sol"])
    in_run = [i for i in range(end + 1) if order[i] != site_k and int(rows[order[i]]["sol"]) == last_sol]
    in_path = [i for i in range(len(order)) if order[i] != site_k and int(rows[order[i]]["sol"]) == last_sol]
    print(f"\n3. last sol of the run: {last_sol}")
    print(f"   rows with this sol inside the run: {len(in_run)}; path indices {in_run}")
    print(f"   rows with this sol in the whole path: {len(in_path)}; path indices {in_path}")
    print(f"   file lines of the tied rows in the run: {[order[i] + 2 for i in in_run]}")
    print(f"   file order matches path order among them: {[order[i] for i in in_run] == sorted(order[i] for i in in_run)}")
    print(f"   the last point is path index {end}: the tied row that comes latest in the file: {end == in_run[-1] and order[end] == max(order[i] for i in in_run)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
