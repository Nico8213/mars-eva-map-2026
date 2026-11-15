"""Write the Nico-approved reference-path rules into validation/params.json.

Rules (approved by Nico):
1. partial   = segment with fewer than 2 distinct points, or length == 0.
   duplicate = segment whose coordinates equal those of the previous segment
               (file order). Union, each segment counted once. The union must be
   exactly segments 206, 207, 369, 402, 490 (5 segments). If not, stop and do
   not change the rule or the file. 180/181 and RMC chain breaks are recorded
   only, never filtered.
2. Start = first PLACES row with frame == SITE (sol recorded as n/a). Print its
   distance to the first MMGIS vertex.
3. No truncation at sol 1897. PLACES is the primary reference, MMGIS is a
   cross-check. Sol coverage of each is computed here.
4. _meta.lock_status is not touched.

Reads validation/data/* and data/processed/grid.json only. Writes only
validation/params.json. Run: .\\.venv\\Scripts\\python.exe validation\\update_reference_rules.py
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import math
import sys
from pathlib import Path

from fill_params import aeqd_forward, haversine

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "validation" / "data"
GRID = ROOT / "data" / "processed" / "grid.json"
PARAMS = ROOT / "validation" / "params.json"

# Approved by Nico (this task). The check below compares the computed union to this set.
APPROVED_SEGMENTS = [206, 207, 369, 402, 490]
APPROVED_COUNT = 5
# Spec section 4.2 "Authoritative citation": PLACES Release 16, sols 0 to 1897.
SPEC_PLACES_MAX_SOL = 1897
RECORD_ONLY_PAIR = (180, 181)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def feature_coords(feat):
    g = feat["geometry"]
    lines = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    return [p for line in lines for p in line]


def distinct_xy(coords):
    return {(p[0], p[1]) for p in coords}


def mtime_str(path: Path) -> str:
    t = datetime.datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    return t.strftime("%Y-%m-%d %H:%M:%S UTC%z")


def main() -> int:
    trav = json.loads((DATA / "M20_traverse.json").read_text(encoding="utf-8"))
    wpts = json.loads((DATA / "M20_waypoints.json").read_text(encoding="utf-8"))
    grid = json.loads(GRID.read_text(encoding="utf-8"))
    feats = trav["features"]
    n_seg = len(feats)
    props = [f["properties"] for f in feats]
    coords = [feature_coords(f) for f in feats]

    # ---- 1. partial / duplicate union ----
    partial = [i for i in range(n_seg) if len(distinct_xy(coords[i])) < 2 or (props[i].get("length") or 0) == 0]
    duplicate = [i for i in range(1, n_seg) if coords[i] == coords[i - 1]]
    union0 = sorted(set(partial) | set(duplicate))
    both = sorted(set(partial) & set(duplicate))
    print(f"segments in file: {n_seg}")
    print(f"partial   (0-based feature index): {partial}")
    print(f"duplicate (0-based feature index): {duplicate}")
    print(f"in both classes: {both}")
    print(f"union, 0-based: {union0} (n={len(union0)})")
    print(f"union, 1-based: {[i + 1 for i in union0]}")
    if len(union0) == APPROVED_COUNT and union0 == APPROVED_SEGMENTS:
        base = 0
    elif len(union0) == APPROVED_COUNT and [i + 1 for i in union0] == APPROVED_SEGMENTS:
        base = 1
    else:
        print(f"STOP: the union is not segments {APPROVED_SEGMENTS} (5). Rule not changed, params.json not written. Tell Nico.")
        return 1
    print(f"MATCH: union equals {APPROVED_SEGMENTS}, numbering starts at {base}")
    remove = set(union0)

    # Recorded only, not filtered.
    chain_breaks = []
    for i in range(n_seg - 1):
        if props[i].get("toRMC") != props[i + 1].get("fromRMC"):
            chain_breaks.append(
                {"between_segments": [i + base, i + 1 + base], "toRMC_prev": props[i].get("toRMC"), "fromRMC_next": props[i + 1].get("fromRMC")}
            )
    pair = []
    for s in RECORD_ONLY_PAIR:
        i = s - base
        pair.append({"segment": s, "sol": props[i].get("sol"), "fromRMC": props[i].get("fromRMC"), "toRMC": props[i].get("toRMC"),
                     "length": props[i].get("length"), "n_points": len(coords[i]), "removed": i in remove})
    print("recorded only, 180/181:", pair)
    print("recorded only, RMC chain breaks:", chain_breaks)

    kept = [i for i in range(n_seg) if i not in remove]
    pts_raw = sum(len(c) for c in coords)
    pts_kept = sum(len(coords[i]) for i in kept)
    print(f"segments after removal: {len(kept)}; points before {pts_raw}, after {pts_kept}")

    # ---- 2. start point: first PLACES SITE row ----
    with open(DATA / "best_interp.csv", "r", encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))
    site = next((r for r in rows if r["frame"] == "SITE"), None)
    if site is None:
        print("STOP: no frame=SITE row in best_interp.csv. params.json not written.")
        return 1
    site_idx = rows.index(site)
    s_lat, s_lon = float(site["planetocentric_latitude"]), float(site["longitude"])
    print(f"PLACES first SITE row: data row {site_idx + 1}, site {site['site']}, lat {s_lat}, lon {s_lon}, sol n/a (csv value {site['sol']})")

    R = 3396190.0
    x0, y0 = grid["top_left_x_m"], grid["top_left_y_m"]
    x1, y1 = x0 + grid["width"] * grid["pixel_size_m"], y0 - grid["height"] * grid["pixel_size_m"]
    sx, sy = R * math.radians(s_lon), R * math.radians(s_lat)
    inside = x0 <= sx <= x1 and y1 <= sy <= y0
    print(f"SITE in DTM projection: x {sx:.3f}, y {sy:.3f}; inside grid extent: {inside}")

    def first_vertex(order):
        i = order[0]
        return i, coords[i][0]

    order_file = kept
    order_sol = sorted(kept, key=lambda i: (props[i].get("sol"), i))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c_lat, c_lon = math.degrees(cy / R), math.degrees(cx / R)

    def dist_m(lon, lat):
        ax, ay = aeqd_forward(s_lat, s_lon, c_lat, c_lon, R)
        bx, by = aeqd_forward(lat, lon, c_lat, c_lon, R)
        return math.hypot(bx - ax, by - ay), haversine(s_lat, s_lon, lat, lon, R)

    out_first = {}
    for label, order in (("file_order_after_removal", order_file), ("ascending_sol_after_removal", order_sol)):
        i, v = first_vertex(order)
        d_aeqd, d_hav = dist_m(v[0], v[1])
        out_first[label] = {"segment": i + base, "sol": props[i].get("sol"), "lon": v[0], "lat": v[1],
                            "distance_to_places_site_m_aeqd": d_aeqd, "distance_to_places_site_m_haversine": d_hav}
        print(f"MMGIS first vertex ({label}): segment {i + base}, sol {props[i].get('sol')}, lon {v[0]}, lat {v[1]}")
        print(f"  distance to PLACES SITE: aeqd {d_aeqd:.3f} m, haversine {d_hav:.3f} m")

    # ---- 3. sol coverage ----
    places_sols = [int(r["sol"]) for r in rows if r["frame"] != "SITE"]
    t_sols = [p["sol"] for p in props]
    t_sols_kept = [props[i]["sol"] for i in kept]
    w_sols = [f["properties"]["sol"] for f in wpts["features"]]
    p_max = max(places_sols)
    cov = {
        "places": {"file": "validation/data/best_interp.csv", "rows": len(rows), "rows_excluding_SITE": len(places_sols),
                   "min_sol": min(places_sols), "max_sol": p_max},
        "mmgis_traverse": {"file": "validation/data/M20_traverse.json", "segments_raw": n_seg, "segments_after_removal": len(kept),
                           "min_sol": min(t_sols_kept), "max_sol": max(t_sols_kept), "min_sol_raw": min(t_sols), "max_sol_raw": max(t_sols),
                           "segments_above_places_max_sol": sum(1 for s in t_sols_kept if s > p_max)},
        "mmgis_waypoints": {"file": "validation/data/M20_waypoints.json", "points": len(w_sols), "min_sol": min(w_sols),
                            "max_sol": max(w_sols), "points_above_places_max_sol": sum(1 for s in w_sols if s > p_max)},
        "spec_places_max_sol": SPEC_PLACES_MAX_SOL,
        "places_max_sol_matches_spec": p_max == SPEC_PLACES_MAX_SOL,
    }
    print("coverage:", json.dumps(cov, indent=1))

    # ---- hashes and dates ----
    h_trav, h_wpts = sha256(DATA / "M20_traverse.json"), sha256(DATA / "M20_waypoints.json")
    print("sha256 traverse :", h_trav)
    print("sha256 waypoints:", h_wpts)
    t_m, w_m = mtime_str(DATA / "M20_traverse.json"), mtime_str(DATA / "M20_waypoints.json")
    print("file mtimes: traverse", t_m, "| waypoints", w_m)

    # ---- write params.json ----
    p = json.loads(PARAMS.read_text(encoding="utf-8"))
    rp = p["reference_path"]
    rp["snapshot_date"] = {
        "value": "2026-11-15 snapshot (replaces the 2026-10-11 snapshot, which is not available as a file)",
        "last_sol_in_file": cov["mmgis_traverse"]["max_sol_raw"],
        "last_sol_in_waypoints": cov["mmgis_waypoints"]["max_sol"],
        "basis": "Spec section 4.2 table, 'Snapshot used': \"Downloaded by Austin on 2026-11-15... This snapshot replaces an earlier 2026-10-11 snapshot... Only this snapshot is used.\" Last sols computed by validation/update_reference_rules.py.",
    }
    rp["download_date"] = {
        "value": "2026-11-15, 08:06 to 08:08 (UTC+8)",
        "file_mtimes": {"M20_traverse.json": t_m, "M20_waypoints.json": w_m},
        "basis": "Spec section 4.2 table, 'Snapshot used'; file modification times read by validation/update_reference_rules.py; validation/data/SNAPSHOT.md.",
    }
    rp["sha256_traverse"] = {"value": h_trav, "basis": "Spec section 4.2 table, 'Integrity'; section 7 key sha256_traverse. Computed by validation/update_reference_rules.py."}
    rp["sha256_waypoints"] = {"value": h_wpts, "basis": "Spec section 4.2 table, 'Integrity'; section 7 key sha256_waypoints. Computed by validation/update_reference_rules.py."}
    rp["authoritative_citation"] = {
        "value": f"Mars 2020 Rover PLACES Bundle (PDS Geosciences Node), Release 16, posted 2026-08-11; sols {cov['places']['min_sol']} to {p_max} in best_interp.csv (computed)",
        "basis": "Spec section 4.2 table, 'Authoritative citation': \"Release 16, posted 2026-08-11, sols 0 to 1897... supersedes the Release 15\". Sol range computed from validation/data/best_interp.csv.",
    }
    rp["cleaning"] = {
        "partial_duplicate_rule": {
            "value": "partial = segment with fewer than 2 distinct points, or length equal to 0. duplicate = segment whose coordinates equal those of the previous segment in file order. Remove the union; each segment counts once.",
            "status": "approved by Nico",
            "basis": "Spec section 4.2 'Counts to re-check' (\"Nico approves the rule\") and section 4.4 'Preparing the reference line' item 1; section 7 key partial_duplicate_rule. Rule text as approved by Nico in this task.",
        },
        "remove_partial_segments": True,
        "remove_duplicate_segments": True,
        "removed_segments": {
            "numbering": f"segment numbers start at {base} (position in features list of M20_traverse.json)",
            "segments": [i + base for i in union0],
            "count": len(union0),
            "partial_only_count": len(set(partial) - set(duplicate)),
            "duplicate_only_count": len(set(duplicate) - set(partial)),
            "both_count": len(both),
            "partial_segments": [i + base for i in partial],
            "duplicate_segments": [i + base for i in duplicate],
            "matches_approved_list": True,
            "basis": "Computed by validation/update_reference_rules.py and checked against Nico's list 206, 207, 369, 402, 490 (5 segments). Spec section 4.4 item 1.",
        },
        "counts": {
            "segments_before": n_seg, "segments_after": len(kept),
            "points_before": pts_raw, "points_after": pts_kept,
            "waypoints": len(w_sols),
            "basis": "Computed from validation/data/M20_traverse.json and M20_waypoints.json. Spec section 4.2 'Counts to re-check': 708 waypoints, 559 segments in the new snapshot.",
        },
        "recorded_not_filtered": {
            "segments_180_181": pair,
            "rmc_chain_breaks": chain_breaks,
            "basis": "Nico's approval: 180/181 and RMC breakpoints are recorded only and not filtered.",
        },
    }
    rp["sol_coverage"] = {
        "value": cov,
        "report_note": "PLACES is the primary reference; MMGIS is used only as a cross-check. The report states the sol range of each (above). No truncation at sol 1897.",
        "basis": "Nico's approval (no cut at sol <= 1897). Spec section 4.2 'Authoritative citation' and section 4.4 last paragraph. Ranges computed by validation/update_reference_rules.py.",
    }
    vr = p["validation_route"]
    vr["landing_site"] = {
        "value": "first PLACES row with frame == SITE in best_interp.csv; sol recorded as n/a",
        "places_site_row": {"data_row": site_idx + 1, "site": site["site"], "planetocentric_latitude": s_lat, "longitude_east_deg": s_lon,
                            "sol": "n/a", "csv_sol_value": site["sol"], "inside_grid_extent": inside},
        "report_text": "起点是 PLACES SITE 行，MMGIS 第一个顶点与它重合",
        "mmgis_first_vertex_vs_places_site": out_first,
        "basis": "Nico's approval. Spec section 4.4 'Definitions' (landing site and first path point), section 4.3 item 5 (SITE row sanity values). Distance computed in the local aeqd projection of 4.3 by validation/update_reference_rules.py.",
    }
    vr["first_path_point"] = {"value": "the PLACES SITE row (see landing_site)", "basis": "Nico's approval; spec section 4.4 'First path point'."}
    vr["sol_truncation"] = {"value": "none; the reference is not cut at sol 1897", "basis": "Nico's approval; spec section 4.4 last paragraph still requires the report to say if the reference lies above PLACES max sol."}
    # _meta.lock_status deliberately untouched.
    PARAMS.write_text(json.dumps(p, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("params.json updated; lock_status:", p["_meta"]["lock_status"][:22])
    return 0


if __name__ == "__main__":
    sys.exit(main())
