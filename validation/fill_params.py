"""Fill the section 7 keys of validation/params.json that can be computed.

Spec: docs/research/nico-routing-spec.md, sections 4.3, 4.5 and 7.
Reads data/processed/slope.npy and grid.json (read only). Writes only
validation/params.json. Stops without writing if the CRS check fails.
All values are computed here; none is typed in by hand except the expected
radius, which comes from spec section 4.3 and is the thing being checked.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLOPE = ROOT / "data" / "processed" / "slope.npy"
GRID = ROOT / "data" / "processed" / "grid.json"
PARAMS = ROOT / "validation" / "params.json"

EXPECTED_RADIUS_M = 3396190.0  # spec 4.3 "Planet"
MAX_REL_DIFF = 0.01  # spec 4.3 item 5 / section 7 haversine_check_max_relative_difference
PENDING = "pending_nico_approval"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def haversine(lat1, lon1, lat2, lon2, r):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def aeqd_forward(lat, lon, lat0, lon0, r):
    """Spherical azimuthal equidistant projection centred on (lat0, lon0). Returns x, y in metres."""
    p, p0, dl = math.radians(lat), math.radians(lat0), math.radians(lon - lon0)
    cos_c = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(dl)
    c = math.acos(max(-1.0, min(1.0, cos_c)))
    k = 1.0 if c == 0 else c / math.sin(c)
    x = r * k * math.cos(p) * math.sin(dl)
    y = r * k * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(dl))
    return x, y


def main() -> int:
    grid = json.loads(GRID.read_text(encoding="utf-8"))

    # Step 2: CRS and radius. pyproj and rasterio are not installed, so the
    # sphere radius is read from the SPHEROID["name",a,inv_f] entry of crs_wkt.
    wkt = grid["crs_wkt"]
    m = re.search(r'SPHEROID\["([^"]*)",\s*([0-9.eE+-]+),\s*([0-9.eE+-]+)\]', wkt)
    if not m:
        print("STOP: no SPHEROID entry in crs_wkt. Tell Nico. params.json not written.")
        return 1
    spheroid_name, radius, inv_f = m.group(1), float(m.group(2)), float(m.group(3))
    proj_m = re.search(r'PROJECTION\["([^"]*)"\]', wkt)
    projection = proj_m.group(1) if proj_m else None
    params_wkt = {k: float(v) for k, v in re.findall(r'PARAMETER\["([^"]*)",\s*([0-9.eE+-]+)\]', wkt)}
    print("WKT spheroid:", spheroid_name, "a =", radius, "inverse_flattening =", inv_f)
    print("WKT projection:", projection, params_wkt)
    print("expected radius_m:", EXPECTED_RADIUS_M)
    ok = (
        radius == EXPECTED_RADIUS_M
        and inv_f == 0
        and projection == "Equirectangular"
        and params_wkt.get("standard_parallel_1") == 0
        and params_wkt.get("central_meridian") == 0
        and params_wkt.get("false_easting") == 0
        and params_wkt.get("false_northing") == 0
    )
    if not ok:
        print("STOP: CRS differs from spec 4.3. Tell Nico. params.json not written.")
        return 1
    print("CRS check: OK (sphere R = 3396190 m, equirectangular, lat_ts 0, lon_0 0)")

    # Step 3: haversine vs local aeqd, opposite corners of the grid extent.
    # Inverse equirectangular on a sphere with lat_ts 0, lon_0 0: lon = x / R, lat = y / R.
    x0, y0 = grid["top_left_x_m"], grid["top_left_y_m"]
    px, w, h = grid["pixel_size_m"], grid["width"], grid["height"]
    x1, y1 = x0 + w * px, y0 - h * px

    def inverse_eqc(x, y):
        return math.degrees(y / radius), math.degrees(x / radius)  # lat, lon

    lat_a, lon_a = inverse_eqc(x0, y0)
    lat_b, lon_b = inverse_eqc(x1, y1)
    lat_c, lon_c = inverse_eqc((x0 + x1) / 2, (y0 + y1) / 2)
    tl = grid["top_left_coordinate"]
    print(f"top-left vs grid.json top_left_coordinate: dlat {lat_a - tl['latitude']:.2e} deg, dlon {lon_a - tl['longitude']:.2e} deg")
    d_aeqd, d_hav = None, None
    ax, ay = aeqd_forward(lat_a, lon_a, lat_c, lon_c, radius)
    bx, by = aeqd_forward(lat_b, lon_b, lat_c, lon_c, radius)
    d_aeqd = math.hypot(bx - ax, by - ay)
    d_hav = haversine(lat_a, lon_a, lat_b, lon_b, radius)
    rel = abs(d_hav - d_aeqd) / d_hav
    print(f"corner A (top-left)     lat {lat_a:.6f} lon {lon_a:.6f}")
    print(f"corner B (bottom-right) lat {lat_b:.6f} lon {lon_b:.6f}")
    print(f"haversine distance (m): {d_hav:.3f}")
    print(f"aeqd local distance (m): {d_aeqd:.3f}")
    print(f"relative difference: {rel:.3e} ({rel * 100:.4f} %)")
    if rel >= MAX_REL_DIFF:
        print("STOP: difference is 1 % or more. Tell Nico. params.json not written.")
        return 1
    # Step 1: hashes.
    h_slope = sha256(SLOPE)
    h_grid = sha256(GRID)
    print("sha256 slope.npy :", h_slope)
    print("sha256 grid.json :", h_grid)

    p = json.loads(PARAMS.read_text(encoding="utf-8"))

    p["terrain_integrity"] = {
        "sha256_slope_npy": {
            "value": h_slope,
            "file": "data/processed/slope.npy",
            "basis": "Spec section 4.3, 'Known limitation of the slope data': \"`params.json` records the SHA-256 of `slope.npy` and `grid.json`\". Section 7 key sha256_slope_npy. Computed by validation/fill_params.py.",
        },
        "sha256_grid_json": {
            "value": h_grid,
            "file": "data/processed/grid.json",
            "basis": "Spec section 4.3, 'Known limitation of the slope data': \"`params.json` records the SHA-256 of `slope.npy` and `grid.json`\". Section 7 key sha256_grid_json. Computed by validation/fill_params.py.",
        },
    }

    p["coordinate_system"]["crs_check"] = {
        "projection": projection,
        "radius_m": radius,
        "inverse_flattening": inv_f,
        "expected_radius_m": EXPECTED_RADIUS_M,
        "matches_spec": True,
        "read_with": "regex on the SPHEROID and PROJECTION entries of grid.json crs_wkt (rasterio and pyproj not installed)",
        "basis": "Spec section 4.3 'What the terrain file is', last bullet: read the CRS and radius from the grid file from grid.json crs_wkt and confirm they equal the spec values. Section 7 key crs.radius_m.",
    }
    p["coordinate_system"]["haversine_check"] = {
        "corner_a_top_left": {"lat_deg": lat_a, "lon_deg": lon_a},
        "corner_b_bottom_right": {"lat_deg": lat_b, "lon_deg": lon_b},
        "aeqd_centre": {"lat_deg": lat_c, "lon_deg": lon_c},
        "aeqd_definition": "spherical azimuthal equidistant, closed-form, same sphere, equivalent to +proj=aeqd +R=radius at aeqd_centre",
        "haversine_distance_m": d_hav,
        "aeqd_distance_m": d_aeqd,
        "relative_difference": rel,
        "max_relative_difference": MAX_REL_DIFF,
        "passed": True,
        "basis": "Spec section 4.3 item 5, second check: \"the great-circle (haversine) distance on the sphere and the distance in the local projection differ by less than 1%\". Section 7 key crs.haversine_check_max_relative_difference = 0.01.",
    }

    c = p["reference_path"]["cleaning"]
    c["partial_duplicate_rule"] = {
        "value": PENDING,
        "basis": "Spec section 4.2 'Counts to re-check' and section 4.4 'Preparing the reference line' item 1; section 7 key reference.partial_duplicate_rule. Left for Nico to approve.",
    }
    c["remove_partial_segments"] = PENDING
    c["remove_duplicate_segments"] = PENDING
    c["spec_stated_removals"] = {
        "partial": 5,
        "duplicate": 1,
        "note": "Numbers as written in spec section 4.2; not adopted until Nico approves.",
    }
    c["status"] = "pending_nico_approval; counts must be confirmed by the script; see missing"

    p["_meta"]["lock_status"] = p["_meta"]["lock_status"]  # unchanged on purpose

    PARAMS.write_text(json.dumps(p, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("params.json updated:", PARAMS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
