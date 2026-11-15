"""Read-only facts about the 2026-11-15 Perseverance snapshot.

Reads only files under validation/data/ (plus, as text, the spec and
validation/check_transform.py for items 2 and 4). Writes nothing.
Run: .\\.venv\\Scripts\\python.exe validation\\read_snapshot_facts.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "validation" / "data"
SPEC = ROOT / "docs" / "research" / "nico-routing-spec.md"
CHECK = ROOT / "validation" / "check_transform.py"


def load(name):
    with open(DATA / name, "r", encoding="utf-8") as h:
        return json.load(h)


def segments(traverse):
    """List of (feature_index, sol, coords) in file order."""
    out = []
    for i, f in enumerate(traverse["features"]):
        g = f["geometry"]
        lines = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        coords = [p for line in lines for p in line]
        out.append((i, f["properties"].get("sol"), coords, f["properties"]))
    return out


def item1(segs, waypoints):
    print("== 1. First vertex of M20_traverse.json (file order) ==")
    i, sol, coords, _ = segs[0]
    print(f"segment index {i}, vertex index 0, sol {sol}, lon {coords[0][0]}, lat {coords[0][1]}")
    t_sols = [s[1] for s in segs]
    print(f"smallest sol in traverse: {min(t_sols)}; sol 0 in traverse: {0 in t_sols}")
    w_feats = waypoints["features"]
    w_sols = [f["properties"].get("sol") for f in w_feats]
    print(f"smallest sol in waypoints: {min(w_sols)}; sol 0 in waypoints: {0 in w_sols}")
    k = w_sols.index(min(w_sols))
    print(f"waypoint index {k} (smallest sol) coords {w_feats[k]['geometry']['coordinates'][:2]}")


def item2(segs):
    print("\n== 2. Partial / duplicate segments ==")
    print("Spec text mentioning the rule (4.2, 4.4):")
    for n, line in enumerate(SPEC.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"partial|duplicate", line, re.I):
            print(f"  spec line {n}: {line.strip()[:160]}")
    print("The spec gives only the counts (5 partial, 1 duplicate) and no rule.")
    print("Not classifying. Candidate indicators below (candidates only):")

    # Candidate A: identical geometry
    by_geom = defaultdict(list)
    for i, sol, coords, _ in segs:
        by_geom[json.dumps(coords)].append(i)
    dup_geom = [v for v in by_geom.values() if len(v) > 1]
    print(f"  A. identical coordinate list: groups {dup_geom}")

    # Candidate B: same (fromRMC, toRMC)
    by_rmc = defaultdict(list)
    for i, sol, coords, p in segs:
        by_rmc[(p.get("fromRMC"), p.get("toRMC"))].append(i)
    print(f"  B. same fromRMC/toRMC pair: groups {[v for v in by_rmc.values() if len(v) > 1]}")

    # Candidate C: same sol
    by_sol = defaultdict(list)
    for i, sol, coords, _ in segs:
        by_sol[sol].append(i)
    print(f"  C. same sol (not necessarily a duplicate): {[(s, v) for s, v in by_sol.items() if len(v) > 1]}")

    # Candidate D: chain break (toRMC of previous != fromRMC of next) - possible partial marker
    breaks = []
    for a, b in zip(segs, segs[1:]):
        if a[3].get("toRMC") != b[3].get("fromRMC"):
            breaks.append((a[0], b[0], a[3].get("toRMC"), b[3].get("fromRMC")))
    print(f"  D. RMC chain breaks (prev.toRMC != next.fromRMC): {breaks}")

    # Candidate E: very short / one distinct point
    short = [(i, len(c), len({tuple(p[:2]) for p in c}), p.get("length")) for i, s, c, p in segs
             if len({tuple(q[:2]) for q in c}) < 2 or (p.get("length") or 0) == 0]
    print(f"  E. <2 distinct points or length 0 (index, n, distinct, length): {short}")

    # Candidate F: sol decreases along file order
    dec = [(a[0], b[0], a[1], b[1]) for a, b in zip(segs, segs[1:]) if b[1] < a[1]]
    print(f"  F. sol decreases between consecutive segments: {dec}")
    print("  Missing rule: which of A-F (or other) defines 'partial' and 'duplicate',")
    print("  and which of two duplicates to keep. Needs project plan 7.4 / Decisions log #3.")


def item3(segs):
    print("\n== 3. Counts ==")
    n_pts = sum(len(s[2]) for s in segs)
    sols = [s[1] for s in segs]
    print(f"points {n_pts}, segments {len(segs)}, min sol {min(sols)}, max sol {max(sols)}")


def item4():
    print("\n== 4. check_transform.py reads grid/layers lat/lon fields? ==")
    text = CHECK.read_text(encoding="utf-8").splitlines()
    pat = re.compile(r"layers\.json|grid_lat|grid_lon|lat_min|lat_max|lon_min|lon_max|bounds|extent|top_left_coordinate|coordinate_notes|GRID_FIELDS|GRID_PATH")
    for n, line in enumerate(text, 1):
        if pat.search(line):
            print(f"  line {n}: {line.strip()[:150]}")
    reads_layers = any("layers.json" in l for l in text)
    gf = re.search(r"GRID_FIELDS = \((.*?)\)", "\n".join(text), re.S)
    fields = re.findall(r'"(\w+)"', gf.group(1)) if gf else []
    latlon = [f for f in fields if re.search(r"lat|lon", f, re.I)]
    print(f"  grid.json fields read: {fields}")
    print(f"  lat/lon fields among them: {latlon}")
    print(f"  reads layers.json: {reads_layers}")
    print(f"  ANSWER: {'有' if (latlon or reads_layers) else '没有'}")


def item5():
    print("\n== 5. best_interp.csv ==")
    with open(DATA / "best_interp.csv", "r", encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))
        header = list(rows[0].keys()) if rows else []
    print(f"header: {header}")
    print(f"data rows (excluding header): {len(rows)}")
    site = [r for r in rows if r["frame"] == "SITE"]
    print(f"frame=SITE rows: {len(site)}")
    for r in site:
        print(f"  planetocentric_latitude {r['planetocentric_latitude']}, "
              f"longitude {r['longitude']}, sol {r['sol']}")


def main():
    traverse = load("M20_traverse.json")
    waypoints = load("M20_waypoints.json")
    segs = segments(traverse)
    item1(segs, waypoints)
    item2(segs)
    item3(segs)
    item4()
    item5()
    return 0


if __name__ == "__main__":
    sys.exit(main())
