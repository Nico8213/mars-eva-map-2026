"""Read-only. Checks behind the PLACES path-row filter. Writes nothing.

Path = rows with frame == ROVER, ascending sol, ties in file order.
Start = first frame == SITE row.
Run: .\\.venv\\Scripts\\python.exe validation\\print_path_checks.py
"""
from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def main() -> int:
    with open(DATA / "best_interp.csv", "r", encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))
    # File line number of data row k (0-based) is k + 2 (line 1 is the header).
    print("frame counts:", dict(collections.Counter(r["frame"] for r in rows)))
    rover = [(k, int(r["sol"])) for k, r in enumerate(rows) if r["frame"] == "ROVER"]
    sols = [s for _, s in rover]
    print(f"\nROVER rows: {len(rover)}; sol min {min(sols)}, sol max {max(sols)}")

    dec = [(rover[i][0] + 2, rover[i + 1][0] + 2, rover[i][1], rover[i + 1][1])
           for i in range(len(rover) - 1) if rover[i + 1][1] < rover[i][1]]
    print(f"ROVER sol nondecreasing along file order: {not dec}")
    if dec:
        print("decreases (file line before, file line after, sol before, sol after):")
        for d in dec:
            print("  ", d)
    stable = sorted(rover, key=lambda t: t[1])
    print(f"stable sort by sol changes the order: {stable != rover}")
    ties = collections.Counter(sols)
    print(f"distinct sols {len(ties)}; sols with more than one row: {sum(1 for c in ties.values() if c > 1)}")

    print("\nsol and dist_total fields:")
    for name in ("M20_traverse.json", "M20_waypoints.json"):
        fc = json.loads((DATA / name).read_text(encoding="utf-8"))
        cnt = collections.Counter(k for f in fc["features"] for k in f["properties"])
        n = len(fc["features"])
        dt = [k for k in cnt if k.startswith("dist_total")]
        print(f"  {name} ({n} features): 'sol' in properties: {'sol' in cnt} ({cnt.get('sol', 0)}/{n}); "
              f"dist_total field(s): {dt if dt else 'none'}" + "".join(f" ({cnt[k]}/{n})" for k in dt))

    site = next((k, r) for k, r in enumerate(rows) if r["frame"] == "SITE")
    k, r = site
    print(f"\nstart point = first SITE row (file line {k + 2}): site {r['site']}, sol {r['sol']} (recorded as n/a), "
          f"planetocentric_latitude {r['planetocentric_latitude']}, longitude {r['longitude']}")
    print(f"other SITE rows (not in path): {sum(1 for x in rows if x['frame'] == 'SITE') - 1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
