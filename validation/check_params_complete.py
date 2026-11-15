"""Read-only. Check validation/params.json against the spec 4.8 list.

Prints OK or MISSING for each required item, and whether every leaf dict
with a value carries a basis. Writes nothing. Exit code 1 if anything is missing.
Run: .\\.venv\\Scripts\\python.exe validation\\check_params_complete.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PARAMS = Path(__file__).resolve().parent / "params.json"

# (spec 4.8 item, JSON path)
REQUIRED = [
    ("slope limit", "slope/slope_limit_deg/value"),
    ("cost formula", "cost_function/formula/value"),
    ("connectivity", "cost_function/connectivity/value"),
    ("connectivity fully_connected", "cost_function/connectivity/fully_connected"),
    ("connectivity geometric", "cost_function/connectivity/geometric"),
    ("grid extent and pixel size", "grid/pixel_size_and_extent/values/width"),
    ("grid corner convention", "grid/pixel_size_and_extent/corner_convention/conclusion"),
    ("terrain resampling", "grid/terrain_resampling/value"),
    ("line resampling", "comparison/line_resampling/value"),
    ("blocked value", "cost_function/blocked_value/value"),
    ("nodata blocked", "slope/nodata_rule/value"),
    ("tolerance primary", "tolerance/d_tol_primary_m/value"),
    ("tolerance sensitivity", "tolerance/d_tol_sensitivity_m/value"),
    ("M1 thresholds", "tolerance/verdict_thresholds_M1/close_match/min_inclusive"),
    ("r_snap", "validation_route/snap/r_snap_cells"),
    ("PLACES download time", "reference_path/places/download_time/value"),
    ("PLACES bytes", "reference_path/places/bytes/value"),
    ("PLACES rows", "reference_path/places/data_rows/value"),
    ("PLACES sha256", "reference_path/places/sha256/value"),
    ("PLACES columns used", "reference_path/places/columns_used/value"),
    ("PLACES path-row filter", "reference_path/places/path_rows/value"),
    ("PLACES frame counts", "reference_path/places/path_rows/frame_counts"),
    ("MMGIS traverse file name", "reference_path/files/traverse_file"),
    ("MMGIS waypoints file name", "reference_path/files/waypoints_file"),
    ("MMGIS traverse sha256", "reference_path/sha256_traverse/value"),
    ("MMGIS waypoints sha256", "reference_path/sha256_waypoints/value"),
    ("slope.npy sha256", "terrain_integrity/sha256_slope_npy/value"),
    ("grid.json sha256", "terrain_integrity/sha256_grid_json/value"),
    ("partial/duplicate rule", "reference_path/cleaning/partial_duplicate_rule/value"),
    ("partial segments", "reference_path/cleaning/partial_duplicate_rule/partial_segments"),
    ("duplicate segments", "reference_path/cleaning/partial_duplicate_rule/duplicate_segments"),
    ("union segments", "reference_path/cleaning/partial_duplicate_rule/union_segments"),
    ("union count", "reference_path/cleaning/partial_duplicate_rule/union_count"),
    ("landing site rule", "validation_route/landing_site/value"),
    ("terrain file", "coordinate_system/terrain_file/official_product_name/value"),
    ("terrain version", "coordinate_system/terrain_file/version/value"),
    ("DTM projection", "coordinate_system/crs_check/projection"),
    ("DTM radius", "coordinate_system/crs_check/radius_m"),
    ("distance projection", "coordinate_system/distance_projection/value"),
    ("1% check relative difference", "coordinate_system/haversine_check/relative_difference"),
    ("1% check passed", "coordinate_system/haversine_check/passed"),
    ("licence", "reference_path/licence/value"),
    ("MMGIS latitude wording", "reference_path/mmgis_latitude/value"),
    ("end_point_error note", "comparison/metrics/end_point_error_m/report_note"),
    ("missing is empty", "missing"),
]


def get(d, path):
    for k in path.split("/"):
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return False, None
    return True, d


def basis_gaps(o, path=""):
    """Dicts that hold a 'value' but no 'basis'."""
    gaps = []
    if isinstance(o, dict):
        if "value" in o and "basis" not in o:
            gaps.append(path or "/")
        for k, v in o.items():
            gaps += basis_gaps(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            gaps += basis_gaps(v, f"{path}[{i}]")
    return gaps


def main() -> int:
    p = json.loads(PARAMS.read_text(encoding="utf-8"))
    bad = 0
    for name, path in REQUIRED:
        ok, v = get(p, path)
        if path == "missing":
            ok = ok and v == []
        elif ok and v is None:
            ok = False
        print(("OK      " if ok else "MISSING ") + f"{name}  [{path}]")
        bad += not ok
    gaps = basis_gaps(p)
    print("entries with value but no basis:", gaps if gaps else "none")
    print("lock_status:", p["_meta"]["lock_status"][:22])
    return 1 if (bad or gaps) else 0


if __name__ == "__main__":
    sys.exit(main())
