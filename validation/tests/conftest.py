"""Shared test support for validation/tests.

Provides a temporary repository root with small synthetic copies of the inputs
of validation/run_validation.py, and a guard that keeps the real
validation/out/report.json from ever existing during tests.
"""

import copy
import csv
import hashlib
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

REAL_ROOT = Path(__file__).resolve().parents[2]
REAL_REPORT = REAL_ROOT / "validation" / "out" / "report.json"

# Make validation/ importable for tests, as test_check_transform.py does.
_VALIDATION_DIR = str(REAL_ROOT / "validation")
if _VALIDATION_DIR not in sys.path:
    sys.path.insert(0, _VALIDATION_DIR)

RADIUS_M = 3396190.0
PLACES_COLUMNS = [
    "frame", "site", "drive", "pose", "landing_x", "landing_y", "landing_z",
    "northing", "easting", "planetocentric_latitude", "planetodetic_latitude",
    "longitude", "elevation", "map_pixel_line", "map_pixel_sample",
    "dem_pixel_line", "dem_pixel_sample", "roll", "pitch", "yaw", "quat_s",
    "quat_v1", "quat_v2", "quat_v3", "areoid", "radius", "sclk", "sol",
]


def sha256_upper(path):
    """Upper-case hex SHA-256 of the file bytes (same form as params.json)."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


@pytest.fixture(autouse=True)
def _real_report_guard():
    """Fail a test if the real validation/out/report.json exists before or after it."""
    assert not REAL_REPORT.exists(), f"{REAL_REPORT} exists before the test"
    yield
    assert not REAL_REPORT.exists(), f"{REAL_REPORT} exists after the test"


@dataclass
class SyntheticRepo:
    root: Path
    params_path: Path
    config_path: Path
    grid_path: Path
    slope_path: Path
    places_path: Path
    out_dir: Path
    report_path: Path
    params: dict
    grid: dict
    slope: np.ndarray
    # (lon, lat) of the PLACES points in file order of the ROVER rows
    inside_count: int


def _dtm_to_lonlat(e, n):
    return math.degrees(e / RADIUS_M), math.degrees(n / RADIUS_M)


def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def build_synthetic_repo(root, width=40, height=40, pixel=1.0):
    """Create a synthetic repository under root and return a SyntheticRepo."""
    root = Path(root)
    top_x, top_y = 4587600.0, 1096600.0

    grid = {
        "source_product": "SYNTHETIC",
        "version": "000",
        "doi": "none",
        "crs_wkt": (
            'PROJCS["Equirectangular Mars 2000 Sphere IAU",GEOGCS["D_Mars_2000_Sphere",'
            'DATUM["Mars_2000_(Sphere)",SPHEROID["Mars_2000_Sphere_IAU",3396190,0]],'
            'PRIMEM["Reference_Meridian",0],UNIT["degree",0.0174532925199433]],'
            'PROJECTION["Equirectangular"]]'
        ),
        "top_left_x_m": top_x,
        "top_left_y_m": top_y,
        "pixel_size_m": pixel,
        "width": width,
        "height": height,
    }
    grid_path = root / "data" / "processed" / "grid.json"
    _write_json(grid_path, grid)

    rng = np.random.default_rng(0)
    slope = rng.uniform(0.0, 10.0, size=(height, width)).astype(np.float32)
    slope_path = root / "data" / "processed" / "slope.npy"
    slope_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(slope_path, slope)

    # PLACES-like CSV: SITE row, rover rows inside the grid, then one outside.
    def row(frame, e, n, sol, site="1", drive="0"):
        lon, lat = _dtm_to_lonlat(e, n)
        r = {c: "0" for c in PLACES_COLUMNS}
        r.update(frame=frame, site=site, drive=drive, pose="-1", sol=str(sol),
                 planetocentric_latitude=f"{lat:.9f}", longitude=f"{lon:.9f}")
        return r

    rows = [row("SITE", top_x + 2.5, top_y - 2.5, -1)]
    inside_pts = [(top_x + 2.5 + 3 * k, top_y - 2.5 - 2 * k) for k in range(1, 6)]
    for k, (e, n) in enumerate(inside_pts, start=1):
        rows.append(row("ROVER", e, n, k, drive=str(k)))
    rows.append(row("ROVER", top_x + width * pixel + 50.0, top_y - 10.0, 6, drive="6"))
    places_path = root / "validation" / "data" / "best_interp.csv"
    places_path.parent.mkdir(parents=True, exist_ok=True)
    with places_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=PLACES_COLUMNS)
        w.writeheader()
        w.writerows(rows)

    # Router config (same keys as routing/config.json, values copied from the real file).
    real_cfg = json.loads((REAL_ROOT / "routing" / "config.json").read_text(encoding="utf-8"))
    config_path = root / "routing" / "config.json"
    _write_json(config_path, real_cfg)

    # Route_Module copy, so run(root, argv) can import routing/route.py under the temp root.
    shutil.copyfile(REAL_ROOT / "routing" / "route.py", root / "routing" / "route.py")

    cx = top_x + width * pixel / 2.0
    cy = top_y - height * pixel / 2.0
    c_lon, c_lat = _dtm_to_lonlat(cx, cy)
    last = len(inside_pts)  # path index of last inside point (SITE is index 0)

    params = {
        "_meta": {"lock_status": "LOCKED v1.0"},
        "slope": {
            "slope_limit_deg": {"value": 20, "note": "synthetic slope limit note"},
            "confidence_layer": {"value": "not used in v1; synthetic limitation text"},
        },
        "cost_function": {
            "cost_base": {"value": 1.0},
            "cost_coefficient": {"value": 1.0},
            "cost_exponent": {"value": 2.0},
            "connectivity": {"value": 8},
            "corner_cutting": {"value": "synthetic corner cutting text"},
        },
        "grid": {"tolerance_floor_rule": {"value": "d_tol >= 2 x pixel size"}},
        "coordinate_system": {
            "crs_check": {"projection": "Equirectangular", "radius_m": RADIUS_M},
            "haversine_check": {"max_relative_difference": 0.01},
            "distance_projection": {
                "centre": {"lat_deg": c_lat, "lon_deg": c_lon},
            },
            "terrain_file": {
                "source_product": {"value": "SYNTHETIC"},
                "version": {"value": "000"},
            },
        },
        "reference_path": {
            "places": {
                "file": {"value": "validation/data/best_interp.csv"},
                "sha256": {"value": sha256_upper(places_path)},
                "columns_used": {"value": ["planetocentric_latitude", "longitude"]},
            },
            "authoritative_citation": {"value": "synthetic PLACES release"},
            "mmgis_latitude": {"value": "synthetic mmgis latitude text"},
        },
        "validation_route": {
            "snap": {"r_snap_cells": 3},
            "locked_reference_segment": {
                "last_point": {
                    "value": {"path_index": last, "file_line": last + 2},
                },
                "segment_used": {
                    "path_index_from": 0,
                    "path_index_to": last,
                    "points": last + 1,
                },
                "recorded_not_explained": {
                    "places_third_segment": {"length_m_aeqd": 1.0},
                    "mmgis_third_segment": {
                        "first_sol": 1, "last_sol": 2, "length_m_aeqd": 2.0,
                    },
                },
            },
        },
        "comparison": {
            "line_resampling": {"spacing_m": 1.0, "value": "synthetic resampling method text"},
            "metrics": {
                "end_point_error_m": {"report_note": "synthetic end point note"},
            },
            "reporting": {"value": "synthetic caveat text"},
        },
        "tolerance": {
            "d_tol_primary_m": {"value": 10},
            "d_tol_sensitivity_m": {"value": [5, 25]},
            "verdict_thresholds_M1": {
                "close_match": {"min_inclusive": 0.8},
                "partial_match": {"min_inclusive": 0.5, "max_exclusive": 0.8},
                "weak_match": {"max_exclusive": 0.5},
            },
        },
        "terrain_integrity": {
            "sha256_slope_npy": {
                "value": sha256_upper(slope_path),
                "file": "data/processed/slope.npy",
            },
            "sha256_grid_json": {
                "value": sha256_upper(grid_path),
                "file": "data/processed/grid.json",
            },
        },
    }
    params_path = root / "validation" / "params.json"
    _write_json(params_path, params)

    out_dir = root / "validation" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    return SyntheticRepo(
        root=root,
        params_path=params_path,
        config_path=config_path,
        grid_path=grid_path,
        slope_path=slope_path,
        places_path=places_path,
        out_dir=out_dir,
        report_path=out_dir / "report.json",
        params=copy.deepcopy(params),
        grid=grid,
        slope=slope,
        inside_count=len(inside_pts) + 1,
    )


@pytest.fixture
def synthetic_repo(tmp_path):
    """A temporary repository root with synthetic inputs and recomputed hashes."""
    return build_synthetic_repo(tmp_path)


@pytest.fixture
def rehash():
    """Return a function that rewrites params.json hashes after a file was changed."""

    def _rehash(repo):
        p = json.loads(repo.params_path.read_text(encoding="utf-8"))
        p["terrain_integrity"]["sha256_slope_npy"]["value"] = sha256_upper(repo.slope_path)
        p["terrain_integrity"]["sha256_grid_json"]["value"] = sha256_upper(repo.grid_path)
        p["reference_path"]["places"]["sha256"]["value"] = sha256_upper(repo.places_path)
        repo.params_path.write_text(json.dumps(p, indent=2), encoding="utf-8")
        repo.params = p
        return p

    return _rehash
