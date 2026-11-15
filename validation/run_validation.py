"""Validation run: our least-cost route against the PLACES reference path.

Run once with `.\\.venv\\Scripts\\python.exe validation\\run_validation.py [--note TEXT ...]`.
All parameters are read from validation/params.json (LOCKED v1.0). Nothing is tuned here.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import importlib.util
import json
import math
import os
import sys
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Named constants. These are the only literals that stand for fixed facts.
# ---------------------------------------------------------------------------

# Task instruction. Not stored in params.json.
LOCKED_COMMIT = "d1965fd"

# Path constants, relative to the repository root.
PARAMS_PATH = Path("validation") / "params.json"
ROUTER_CONFIG_PATH = Path("routing") / "config.json"
GRID_PATH = Path("data") / "processed" / "grid.json"
SLOPE_PATH = Path("data") / "processed" / "slope.npy"
PLACES_PATH = Path("validation") / "data" / "best_interp.csv"
REPORT_PATH = Path("validation") / "out" / "report.json"
ROUTE_MODULE_PATH = Path("routing") / "route.py"

# Read size for hashing files (implementation detail, not a parameter).
HASH_BLOCK_BYTES = 1 << 20

# Fields required in grid.json, same as check_transform.GRID_FIELDS.
GRID_FIELDS = ("top_left_x_m", "top_left_y_m", "pixel_size_m", "width", "height")

# params.json `_meta.lock_status`.
LOCK_STATUS_EXPECTED = "LOCKED v1.0"

# Spec 4.5 floor rule: d_tol_primary_m >= 2 * pixel_size_m.
TOLERANCE_FLOOR_FACTOR = 2

# Spec 4.5 metric M2: 95th percentile.
PERCENTILE_P95 = 95

# Unit conversion: share to percent.
PERCENT_FACTOR = 100

# PLACES file column `frame`.
FRAME_SITE = "SITE"
FRAME_ROVER = "ROVER"

# Data row k is on file line k + 2 (header is line 1), as in print_path_checks.py.
FILE_LINE_OFFSET = 2

# Verdict labels, spec 4.5.
LABEL_CLOSE = "close match"
LABEL_PARTIAL = "partial match"
LABEL_WEAK = "weak match"

# Fixed limitation texts (Requirement 10). Each has its source.

# Source: user's instruction of 2026-11-15 (Requirement 10 criterion 2).
END_ON_BOTTOM_ROW_TEXT = (
    "the reference end point is on the bottom grid row, less than 1 m from the "
    "lower boundary, so the reference path leaves the grid there and does not "
    "stop naturally"
)

# Source: user's instruction of 2026-11-15 (Requirement 10 criterion 4).
EAST_WEST_TEXT = "east-west slope underestimated by about 5%"

# Source: user's instruction of 2026-11-15.
LIMIT_MAX_SLOPE_PIXEL_CENTRES = "max slope is taken at pixel centres"

# Source: user's instruction of 2026-11-15; params.json key
# `cost_function.corner_cutting`; routing/README.md.
LIMIT_CORNER_CUTTING = "8-neighbour moves can cut corners"

# Source: user's instruction of 2026-11-15; params.json keys `reference_path`
# and `validation_route` `last_path_point` `tie_rule`.
LIMIT_NO_DIST_TOTAL = (
    "the traverse has no dist_total, so ties are resolved by file order, "
    "not by distance"
)

# Source: user's instruction of 2026-11-15.
LIMIT_SEGMENT1_LEAVES_GRID = "PLACES segment 1 ends where later points leave the grid"


# ---------------------------------------------------------------------------
# Errors and data classes
# ---------------------------------------------------------------------------


class ValidationAbort(Exception):
    """A check failed. The run stops, no report is written, exit code 2."""


@dataclass(frozen=True)
class Grid:
    top_left_x_m: float
    top_left_y_m: float
    pixel_size_m: float
    width: int
    height: int


@dataclass
class RouteResult:
    status: str
    reason: str | None
    start_cell: tuple[int, int] | None
    end_cell: tuple[int, int] | None
    start_snap_cells: float | None
    end_snap_cells: float | None
    start_clamped: bool
    end_clamped: bool
    path: list[tuple[int, int]] | None
    find_path_cost: float | None
    recomputed_cost: float | None
    length_m: float | None = None  # route length in Local_Projection metres


@dataclass
class Reference:
    index_order: list[int]
    lon: np.ndarray
    lat: np.ndarray
    dtm_en: np.ndarray
    aeqd_xy: np.ndarray


# ---------------------------------------------------------------------------
# Route_Module, imported by path. Only its pure functions are used later.
# write_route, main and get_commit_hash are never called.
# ---------------------------------------------------------------------------


def load_route_module(root: Path):
    """Import routing/route.py under `root` by file path."""
    path = Path(root) / ROUTE_MODULE_PATH
    spec = importlib.util.spec_from_file_location("route_module", path)
    if spec is None or spec.loader is None:
        raise ValidationAbort(f"cannot load Route_Module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses need the module registered
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Key access and lock check
# ---------------------------------------------------------------------------


def require(d, *keys, file):
    """Walk nested keys of `d`. Abort naming `file` and the dotted key path if one is missing."""
    cur = d
    for i, key in enumerate(keys):
        if not isinstance(cur, dict) or key not in cur:
            dotted = ".".join(str(k) for k in keys[: i + 1])
            raise ValidationAbort(f"{file}: missing key {dotted}")
        cur = cur[key]
    return cur


def check_lock(P):
    """Abort unless params.json `_meta.lock_status` is the expected value."""
    status = require(P, "_meta", "lock_status", file=str(PARAMS_PATH))
    if status != LOCK_STATUS_EXPECTED:
        raise ValidationAbort(
            f"{PARAMS_PATH}: _meta.lock_status is {status!r}, expected {LOCK_STATUS_EXPECTED!r}"
        )


# ---------------------------------------------------------------------------
# Input and lock checks. Every input is opened read-only.
# ---------------------------------------------------------------------------


def sha256_file(path):
    """Upper-case hex SHA-256 of the file bytes, to match the locked values."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(HASH_BLOCK_BYTES), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_json(path):
    """Read a JSON file as UTF-8. Abort if it is missing or not parsable."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise ValidationAbort(f"{path}: file is missing") from None
    except (OSError, ValueError) as exc:
        raise ValidationAbort(f"{path}: cannot read as JSON ({exc})") from None


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def load_grid_strict(path):
    """Read grid.json with the same field checks as check_transform.load_grid."""
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValidationAbort(f"{path}: top level must be an object")
    for name in GRID_FIELDS:
        if name not in data:
            raise ValidationAbort(f"{path}: missing key {name}")
    for name in ("top_left_x_m", "top_left_y_m"):
        value = data[name]
        if not _is_number(value) or not math.isfinite(value):
            raise ValidationAbort(f"{path}: invalid value for {name}")
    pixel = data["pixel_size_m"]
    if not _is_number(pixel) or not math.isfinite(pixel) or pixel <= 0:
        raise ValidationAbort(f"{path}: invalid value for pixel_size_m")
    for name in ("width", "height"):
        value = data[name]
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValidationAbort(f"{path}: invalid value for {name}")
    return Grid(
        top_left_x_m=float(data["top_left_x_m"]),
        top_left_y_m=float(data["top_left_y_m"]),
        pixel_size_m=float(pixel),
        width=data["width"],
        height=data["height"],
    )


def load_slope_strict(path):
    """Load the slope raster read-only, without pickle."""
    try:
        return np.load(path, allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise ValidationAbort(f"{path}: cannot load slope raster ({exc})") from None


def load_router_config(route_module, path):
    """Call load_config of the Route_Module unchanged. RoutingError becomes ValidationAbort."""
    try:
        return route_module.load_config(Path(path))
    except route_module.RoutingError as exc:
        raise ValidationAbort(str(exc)) from None


def check_hashes(P, computed):
    """Compare computed SHA-256 values with the locked ones. Abort on any difference.

    `computed` maps "slope", "grid" and "places" to upper-case hex strings.
    Returns the per-file comparison record for the report.
    """
    file = str(PARAMS_PATH)
    locked = {
        "slope": require(P, "terrain_integrity", "sha256_slope_npy", "value", file=file),
        "grid": require(P, "terrain_integrity", "sha256_grid_json", "value", file=file),
        "places": require(P, "reference_path", "places", "sha256", "value", file=file),
    }
    record = {}
    for name, locked_value in locked.items():
        if name not in computed:
            raise ValidationAbort(f"no computed SHA-256 for {name}")
        match = computed[name] == locked_value
        record[name] = {
            "sha256": computed[name],
            "locked_sha256": locked_value,
            "match": match,
        }
    for name, entry in record.items():
        if not entry["match"]:
            raise ValidationAbort(
                f"SHA-256 of {name} differs from the locked value "
                f"(computed {entry['sha256']}, locked {entry['locked_sha256']})"
            )
    return record


def check_floor_rule(d_tol_m, pixel_size_m):
    """Abort if d_tol is below TOLERANCE_FLOOR_FACTOR times the pixel size (spec 4.5)."""
    if d_tol_m < TOLERANCE_FLOOR_FACTOR * pixel_size_m:
        raise ValidationAbort(
            f"tolerance floor rule: d_tol {d_tol_m} m is below "
            f"{TOLERANCE_FLOOR_FACTOR} x pixel size {pixel_size_m} m"
        )


def check_slope_shape(slope, grid):
    """Abort if the slope raster shape is not (height, width) of the grid."""
    expected = (grid.height, grid.width)
    if tuple(slope.shape) != expected:
        raise ValidationAbort(
            f"slope raster shape {tuple(slope.shape)} differs from grid (height, width) {expected}"
        )


def check_rover_sol_order(sols):
    """Abort unless the ROVER sols are non-decreasing in file order."""
    previous = None
    for index, sol in enumerate(sols):
        if previous is not None and sol < previous:
            raise ValidationAbort(
                f"ROVER sol decreases in file order at ROVER row {index}: {sol} after {previous}"
            )
        previous = sol


def check_config_matches(cost_params, P):
    """Abort if the Router_Config values differ from the Params_File values.

    `cost_params` is the CostParams returned by load_config of the Route_Module.
    """
    file = str(PARAMS_PATH)
    expected = {
        "slope_limit_deg": require(P, "slope", "slope_limit_deg", "value", file=file),
        "cost_base": require(P, "cost_function", "cost_base", "value", file=file),
        "cost_coefficient": require(P, "cost_function", "cost_coefficient", "value", file=file),
        "cost_exponent": require(P, "cost_function", "cost_exponent", "value", file=file),
        "connectivity": require(P, "cost_function", "connectivity", "value", file=file),
    }
    for field, locked_value in expected.items():
        actual = getattr(cost_params, field)
        if actual != locked_value:
            raise ValidationAbort(
                f"{ROUTER_CONFIG_PATH} differs from {PARAMS_PATH} in {field}: "
                f"router {actual!r}, params {locked_value!r}"
            )


def require_text(P, *keys):
    """Return a non-empty string at `keys` of the Params_File. Abort naming the key otherwise."""
    value = require(P, *keys, file=str(PARAMS_PATH))
    if not isinstance(value, str) or not value.strip():
        dotted = ".".join(str(k) for k in keys)
        raise ValidationAbort(f"{PARAMS_PATH}: key {dotted} is not a non-empty string")
    return value


# ---------------------------------------------------------------------------
# Projections and grid cells. Radius and centre are arguments, read from
# P["coordinate_system"] by the caller.
# ---------------------------------------------------------------------------


def project_dtm(lon, lat, radius_m):
    """DTM projection (equirectangular on a sphere): used only for cells and extent."""
    return radius_m * math.radians(lon), radius_m * math.radians(lat)


def project_aeqd(lon, lat, centre, radius_m):
    """Spherical azimuthal equidistant projection, closed form.

    `centre` is (lat0_deg, lon0_deg). Returns (x, y) in metres.
    """
    lat0 = math.radians(centre[0])
    lon0 = math.radians(centre[1])
    phi = math.radians(lat)
    dlon = math.radians(lon) - lon0
    cos_c = math.sin(lat0) * math.sin(phi) + math.cos(lat0) * math.cos(phi) * math.cos(dlon)
    cos_c = max(-1.0, min(1.0, cos_c))  # guard acos against rounding
    c = math.acos(cos_c)
    sin_c = math.sin(c)
    k = c / sin_c if sin_c != 0 else 1.0
    x = radius_m * k * math.cos(phi) * math.sin(dlon)
    y = radius_m * k * (
        math.cos(lat0) * math.sin(phi) - math.sin(lat0) * math.cos(phi) * math.cos(dlon)
    )
    return x, y


def dtm_to_aeqd(e, n, centre, radius_m):
    """Invert the DTM projection, then project to the local azimuthal equidistant frame."""
    lon = math.degrees(e / radius_m)
    lat = math.degrees(n / radius_m)
    return project_aeqd(lon, lat, centre, radius_m)


def point_in_extent(e, n, grid):
    """True when (e, n) is inside the grid extent, bounds included."""
    x1 = grid.top_left_x_m + grid.width * grid.pixel_size_m
    y1 = grid.top_left_y_m - grid.height * grid.pixel_size_m
    return grid.top_left_x_m <= e <= x1 and y1 <= n <= grid.top_left_y_m


def point_to_cell(e, n, grid):
    """Floor rule. Returns (row, col, clamped); the maximum edge maps to the last index."""
    col = math.floor((e - grid.top_left_x_m) / grid.pixel_size_m)
    row = math.floor((grid.top_left_y_m - n) / grid.pixel_size_m)
    clamped = False
    if col == grid.width:
        col = grid.width - 1
        clamped = True
    if row == grid.height:
        row = grid.height - 1
        clamped = True
    return row, col, clamped


def cell_centre(row, col, grid, route_module):
    """(easting, northing) of the cell centre, through pixel_to_coord of the Route_Module."""
    route_grid = route_module.Grid(
        pixel_size_m=grid.pixel_size_m,
        width=grid.width,
        height=grid.height,
        easting_m=grid.top_left_x_m,
        northing_m=grid.top_left_y_m,
        crs="",
    )
    return route_module.pixel_to_coord(row, col, route_grid)


# ---------------------------------------------------------------------------
# Reference path
# ---------------------------------------------------------------------------


def read_places_rows(path):
    """Read the PLACES CSV (UTF-8) as a list of dicts in file order. Read-only."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError:
        raise ValidationAbort(f"{path}: file is missing") from None
    except (OSError, ValueError) as exc:
        raise ValidationAbort(f"{path}: cannot read as CSV ({exc})") from None


def order_reference_rows(rows):
    """File row indices of the path: first SITE row, then ROVER rows by stable ascending sol.

    Other SITE rows are dropped. Aborts if there is no SITE row.
    """
    site = next((k for k, r in enumerate(rows) if r["frame"] == FRAME_SITE), None)
    if site is None:
        raise ValidationAbort(f"{PLACES_PATH}: no row with frame {FRAME_SITE}")
    rover = [k for k, r in enumerate(rows) if r["frame"] == FRAME_ROVER]
    rover.sort(key=lambda k: int(rows[k]["sol"]))  # sorted() is stable: ties keep file order
    return [site] + rover


def positions(rows, order):
    """Longitude and latitude arrays (degrees) of the ordered rows.

    Only `planetocentric_latitude` and `longitude` are read.
    """
    lat = np.array([float(rows[k]["planetocentric_latitude"]) for k in order], dtype=float)
    lon = np.array([float(rows[k]["longitude"]) for k in order], dtype=float)
    return lon, lat


def first_run_end(inside_flags):
    """Index of the last True of the first uninterrupted True run. Aborts if the first flag is False."""
    if len(inside_flags) == 0 or not inside_flags[0]:
        raise ValidationAbort("path index 0 is not inside the grid extent")
    end = 0
    while end + 1 < len(inside_flags) and inside_flags[end + 1]:
        end += 1
    return end


def verify_segment(order, flags, locked, rows):
    """Check the locked first in-grid segment. Aborts on any failure; never picks another segment.

    `locked` is `validation_route.locked_reference_segment` of the Params_File.
    Checks: path index 0 inside, all indices up to the locked last index inside,
    the locked last index ends the first in-extent run, the point count, and the
    file line of the last point (file_line = row index + FILE_LINE_OFFSET).
    Returns the locked last path index.
    """
    file = str(PARAMS_PATH)
    seg = require(locked, "segment_used", file=file)
    first = require(seg, "path_index_from", file=file)
    last = require(seg, "path_index_to", file=file)
    points = require(seg, "points", file=file)
    last_line = require(locked, "last_point", "value", "file_line", file=file)

    if len(order) != len(flags):
        raise ValidationAbort("order and in-extent flags differ in length")
    if first != 0:
        raise ValidationAbort(f"locked segment must start at path index 0, not {first}")
    if last >= len(order):
        raise ValidationAbort(f"locked last path index {last} is beyond the path ({len(order)} points)")
    if not flags[first]:
        raise ValidationAbort("path index 0 is not inside the grid extent")
    outside = [i for i in range(first, last + 1) if not flags[i]]
    if outside:
        raise ValidationAbort(f"path index {outside[0]} is outside the grid extent, inside the locked segment")
    run_end = first_run_end(flags)
    if run_end != last:
        raise ValidationAbort(
            f"locked last path index {last} is not the end of the first in-extent run (run ends at {run_end})"
        )
    if last + 1 != points:
        raise ValidationAbort(f"locked point count {points} differs from last index + 1 = {last + 1}")
    actual_line = order[last] + FILE_LINE_OFFSET
    if actual_line != last_line:
        raise ValidationAbort(
            f"last point is on file line {actual_line}, locked file line is {last_line}"
        )
    return last


def build_reference(rows, P, grid):
    """Build the Reference_Path for the locked segment (path index 0 to the locked last index).

    Returns a Reference with lon/lat, DTM metres and local aeqd metres.
    The radius and the aeqd centre come from the Params_File.
    """
    file = str(PARAMS_PATH)
    radius = require(P, "coordinate_system", "crs_check", "radius_m", file=file)
    centre_d = require(P, "coordinate_system", "distance_projection", "centre", file=file)
    centre = (
        require(centre_d, "lat_deg", file=file),
        require(centre_d, "lon_deg", file=file),
    )
    locked = require(P, "validation_route", "locked_reference_segment", file=file)

    order = order_reference_rows(rows)
    lon, lat = positions(rows, order)
    en = np.array([project_dtm(x, y, radius) for x, y in zip(lon, lat)], dtype=float)
    flags = [point_in_extent(e, n, grid) for e, n in en]
    last = verify_segment(order, flags, locked, rows)

    stop = last + 1
    lon, lat, en = lon[:stop], lat[:stop], en[:stop]
    xy = np.array([project_aeqd(x, y, centre, radius) for x, y in zip(lon, lat)], dtype=float)
    return Reference(index_order=order[:stop], lon=lon, lat=lat, dtm_en=en, aeqd_xy=xy)


# ---------------------------------------------------------------------------
# Route: snapping, routing, invalid-run gate
# ---------------------------------------------------------------------------

# Message prefix of the Route_Module error for "no path exists between ...".
NO_PATH_MESSAGE_PREFIX = "no path exists"

STATUS_OK = "ok"
STATUS_SNAPPED = "snapped"
STATUS_UNREACHABLE_ENDPOINT = "unreachable_endpoint"
STATUS_UNREACHABLE = "unreachable"
STATUS_INVALID = "invalid"


def build_route_cost(route_module, slope, cost_params, nodata_value=None):
    """Cost raster from build_cost_raster of the Route_Module."""
    return route_module.build_cost_raster(slope, cost_params, nodata_value)


def snap_cell(cost, cell, r_snap):
    """Nearest unblocked cell within Euclidean cell distance r_snap.

    Returns (cell, distance_in_cells); (cell, 0.0) if the cell is unblocked.
    Ties go to the lowest row, then the lowest column. None if nothing is in range.
    """
    height, width = cost.shape
    row, col = int(cell[0]), int(cell[1])
    if np.isfinite(cost[row, col]):
        return (row, col), 0.0
    reach = math.floor(r_snap)
    best = None  # (distance_squared, row, col)
    limit = r_snap * r_snap
    for r in range(max(0, row - reach), min(height - 1, row + reach) + 1):
        for c in range(max(0, col - reach), min(width - 1, col + reach) + 1):
            d2 = (r - row) ** 2 + (c - col) ** 2
            if d2 > limit or not np.isfinite(cost[r, c]):
                continue
            key = (d2, r, c)
            if best is None or key < best:
                best = key
    if best is None:
        return None
    return (best[1], best[2]), math.sqrt(best[0])


def route_length_m(path, grid, centre, radius_m, route_module):
    """Length of the cell-centre polyline in Local_Projection (aeqd) metres."""
    pts = []
    for r, c in path:
        e, n = cell_centre(r, c, grid, route_module)
        pts.append(dtm_to_aeqd(e, n, centre, radius_m))
    return float(sum(math.dist(a, b) for a, b in zip(pts, pts[1:])))


def run_route(cost, start, end, params, r_snap, *, route_module=None, grid=None,
              centre=None, radius_m=None, start_clamped=False, end_clamped=False):
    """Snap both ends, call find_path at most once, return a RouteResult.

    `params` is the CostParams of the Route_Module (connectivity is used).
    Unreachable results are statuses, not aborts, and are never retried.
    If grid, centre and radius_m are given, the route length is computed.
    """
    if route_module is None:
        route_module = load_route_module(Path(__file__).resolve().parent.parent)

    def result(status, reason=None, **kw):
        base = dict(
            status=status, reason=reason, start_cell=None, end_cell=None,
            start_snap_cells=None, end_snap_cells=None,
            start_clamped=start_clamped, end_clamped=end_clamped,
            path=None, find_path_cost=None, recomputed_cost=None,
        )
        base.update(kw)
        return RouteResult(**base)

    s = snap_cell(cost, start, r_snap)
    e = snap_cell(cost, end, r_snap)
    if s is None or e is None:
        missing = " and ".join(
            name for name, v in (("start", s), ("end", e)) if v is None
        )
        return result(
            STATUS_UNREACHABLE_ENDPOINT,
            f"no unblocked cell within {r_snap} cells of the {missing} cell",
            start_cell=tuple(start) if s is None else s[0],
            end_cell=tuple(end) if e is None else e[0],
            start_snap_cells=None if s is None else s[1],
            end_snap_cells=None if e is None else e[1],
        )
    (s_cell, s_dist), (e_cell, e_dist) = s, e
    ends = dict(start_cell=s_cell, end_cell=e_cell,
                start_snap_cells=s_dist, end_snap_cells=e_dist)
    try:
        path, total = route_module.find_path(cost, s_cell, e_cell, params.connectivity)
    except route_module.RoutingError as exc:
        if str(exc).startswith(NO_PATH_MESSAGE_PREFIX):
            return result(STATUS_UNREACHABLE, str(exc), **ends)
        raise
    status = STATUS_SNAPPED if (s_dist > 0 or e_dist > 0) else STATUS_OK
    length = None
    if grid is not None and centre is not None and radius_m is not None:
        length = route_length_m(path, grid, centre, radius_m, route_module)
    return result(
        status, None, path=path, find_path_cost=total,
        recomputed_cost=route_module.path_cost(cost, path), length_m=length, **ends,
    )


def gate(result, cost, r_snap):
    """Invalid-run gate: status becomes `invalid` with a reason if the cost is not
    finite, a route cell is blocked, or a snap distance exceeds r_snap.

    Only results with status ok or snapped are examined. Both costs stay recorded.
    """
    if result.status not in (STATUS_OK, STATUS_SNAPPED):
        return result
    reasons = []
    for name, value in (("find_path cost", result.find_path_cost),
                        ("recomputed cost", result.recomputed_cost)):
        if value is None or not math.isfinite(value):
            reasons.append(f"{name} is not finite")
    if result.path is not None:
        blocked = [cell for cell in result.path if not np.isfinite(cost[cell[0], cell[1]])]
        if blocked:
            reasons.append(f"route cell {tuple(blocked[0])} is blocked")
    for name, dist in (("start", result.start_snap_cells), ("end", result.end_snap_cells)):
        if dist is not None and dist > r_snap:
            reasons.append(f"{name} snap distance {dist} exceeds {r_snap} cells")
    if reasons:
        result.status = STATUS_INVALID
        result.reason = "; ".join(reasons)
    return result


# ---------------------------------------------------------------------------
# Resampling and distance metrics (pure functions, metres in the aeqd plane)
# ---------------------------------------------------------------------------


def format_tol(value):
    """Key text of a tolerance, e.g. 5.0 -> "5", 2.5 -> "2.5". No tolerance literal."""
    return f"{float(value):g}"


def resample(vertices, spacing):
    """Resample a polyline at equal arc-length steps.

    Positions are 0, spacing, 2*spacing, ... while < total length, then the total
    length is appended, so the last interval is at most `spacing`. First and last
    vertex are exact. A one-vertex or zero-length line returns its first vertex.
    """
    v = np.asarray(vertices, dtype=float).reshape(-1, 2)
    if v.shape[0] == 0:
        raise ValueError("resample needs at least one vertex")
    seg = np.hypot(np.diff(v[:, 0]), np.diff(v[:, 1]))
    s = np.concatenate(([0.0], np.cumsum(seg)))
    total = float(s[-1])
    if v.shape[0] == 1 or total <= 0.0:
        return v[:1].copy()
    if not spacing > 0:
        raise ValueError("spacing must be positive")
    pos = np.concatenate((np.arange(0.0, total, spacing), [total]))
    out = np.column_stack((np.interp(pos, s, v[:, 0]), np.interp(pos, s, v[:, 1])))
    out[0] = v[0]
    out[-1] = v[-1]
    return out


def nearest_distances(a, b):
    """Distance from each point of `a` to the nearest point of `b`."""
    from scipy.spatial import cKDTree

    a = np.asarray(a, dtype=float).reshape(-1, 2)
    b = np.asarray(b, dtype=float).reshape(-1, 2)
    return np.asarray(cKDTree(b).query(a)[0], dtype=float)


def sample_weights(samples):
    """Length represented by each sample: half of each adjacent interval.

    A single sample gets weight 1 (documented edge case). Weights sum to the line length.
    """
    s = np.asarray(samples, dtype=float).reshape(-1, 2)
    if s.shape[0] == 1:
        return np.ones(1)
    step = np.hypot(np.diff(s[:, 0]), np.diff(s[:, 1]))
    w = np.zeros(s.shape[0])
    w[:-1] += step / 2.0
    w[1:] += step / 2.0
    return w


def m0(d):
    d = np.asarray(d, dtype=float)
    return {"mean": float(d.mean()), "max": float(d.max())}


def m2(d):
    d = np.asarray(d, dtype=float)
    return {"median": float(np.median(d)), "p95": float(np.percentile(d, PERCENTILE_P95))}


def overlap(d, w, d_tol):
    """Share of line length within d_tol. Zero-length line: share of samples."""
    d = np.asarray(d, dtype=float)
    w = np.asarray(w, dtype=float)
    within = d <= d_tol
    total = float(w.sum())
    if total <= 0.0:
        return float(within.mean())
    return float(w[within].sum() / total)


def m1(route_s, ref_s, d_tol):
    """Symmetric overlap: M1 is the smaller of the route and reference shares."""
    route_s = np.asarray(route_s, dtype=float).reshape(-1, 2)
    ref_s = np.asarray(ref_s, dtype=float).reshape(-1, 2)
    ov_route = overlap(nearest_distances(route_s, ref_s), sample_weights(route_s), d_tol)
    ov_ref = overlap(nearest_distances(ref_s, route_s), sample_weights(ref_s), d_tol)
    return {
        "d_tol": d_tol,
        "overlap_ref": ov_ref,
        "overlap_route": ov_route,
        "M1": min(ov_route, ov_ref),
    }


def dtw(a, b):
    """Dynamic time warping with steps (1,0), (0,1), (1,1) and Euclidean local cost.

    Returns (total_cost, path_points). Tie order when backtracking: diagonal, then
    (i-1, j), then (i, j-1). M3 = total_cost / path_points.
    """
    a = np.asarray(a, dtype=float).reshape(-1, 2)
    b = np.asarray(b, dtype=float).reshape(-1, 2)
    n, m = a.shape[0], b.shape[0]
    local = np.hypot(a[:, None, 0] - b[None, :, 0], a[:, None, 1] - b[None, :, 1])
    acc = np.full((n + 1, m + 1), np.inf)
    acc[0, 0] = 0.0
    for i in range(1, n + 1):
        prev = acc[i - 1]
        cur = acc[i]
        row = local[i - 1]
        for j in range(1, m + 1):
            cur[j] = row[j - 1] + min(prev[j - 1], prev[j], cur[j - 1])
    i, j = n, m
    points = 1
    while (i, j) != (1, 1):
        options = (
            (acc[i - 1, j - 1], i - 1, j - 1),
            (acc[i - 1, j], i - 1, j),
            (acc[i, j - 1], i, j - 1),
        )
        best = options[0]
        for opt in options[1:]:
            if opt[0] < best[0]:
                best = opt
        _, i, j = best
        points += 1
    return float(acc[n, m]), points


def end_point_errors(route_s, ref_s):
    route_s = np.asarray(route_s, dtype=float).reshape(-1, 2)
    ref_s = np.asarray(ref_s, dtype=float).reshape(-1, 2)
    return {
        "first_m": float(np.linalg.norm(route_s[0] - ref_s[0])),
        "last_m": float(np.linalg.norm(route_s[-1] - ref_s[-1])),
    }


# ---------------------------------------------------------------------------
# Verdict and blocked share of the reference points
# ---------------------------------------------------------------------------

# Statuses with a metric result. Other statuses give a null verdict (Req 7.5).
STATUSES_WITH_RESULT = (STATUS_OK, STATUS_SNAPPED)


def verdict(m1_primary, thresholds):
    """Label of the primary M1. Thresholds are arguments (verdict_thresholds_M1 of params.json).

    m1 >= close_match.min_inclusive -> close; >= partial_match.min_inclusive -> partial;
    otherwise weak.
    """
    close = thresholds["close_match"]["min_inclusive"]
    partial = thresholds["partial_match"]["min_inclusive"]
    if m1_primary >= close:
        return LABEL_CLOSE
    if m1_primary >= partial:
        return LABEL_PARTIAL
    return LABEL_WEAK


def verdict_block(status, m1_primary, thresholds, P):
    """Verdict and caveat for the report. The verdict is None for failed statuses (Req 7.5).

    The caveat is copied from comparison.reporting.value and stored next to the verdict (Req 7.6).
    """
    caveat = require(P, "comparison", "reporting", "value", file=str(PARAMS_PATH))
    label = None
    if status in STATUSES_WITH_RESULT and m1_primary is not None:
        label = verdict(m1_primary, thresholds)
    return {"verdict": label, "caveat": caveat}


def blocked_share(points_en, cost, grid, slope):
    """Share of reference points (DTM metres) whose cell is blocked in the route cost raster.

    Points outside the extent are skipped. Cells come from point_to_cell, as for the route.
    Returns inside, blocked, share, percent (None when inside is 0) and the blocked points
    with path_index, row, col and slope_deg.
    """
    inside = 0
    blocked_points = []
    for index, (e, n) in enumerate(np.asarray(points_en, dtype=float).reshape(-1, 2)):
        if not point_in_extent(e, n, grid):
            continue
        inside += 1
        row, col, _ = point_to_cell(e, n, grid)
        if not np.isfinite(cost[row, col]):
            blocked_points.append({
                "path_index": index,
                "row": int(row),
                "col": int(col),
                "slope_deg": float(slope[row, col]),
            })
    blocked = len(blocked_points)
    share = blocked / inside if inside else None
    percent = PERCENT_FACTOR * share if share is not None else None
    return {
        "inside": inside,
        "blocked": blocked,
        "share": share,
        "percent": percent,
        "points": blocked_points,
    }


# ---------------------------------------------------------------------------
# Limitations and notes
# ---------------------------------------------------------------------------

SEGMENT3_TEMPLATE = (
    "PLACES segment 3 (sol {first_sol}-{last_sol}) {places_len:.3f} m vs "
    "MMGIS {mmgis_len:.3f} m, unexplained; no parameter changed because of it"
)


def end_distance_to_lower_boundary(en_point, grid):
    """Distance in metres of a DTM point (easting, northing) to the lower grid boundary."""
    northing = float(en_point[1])
    return northing - (grid.top_left_y_m - grid.height * grid.pixel_size_m)


def end_distance_run_note(distance_m, grid):
    """Run note with the computed distance when it is not below the pixel size, else None.

    The limitation text END_ON_BOTTOM_ROW_TEXT stays unchanged either way (Req 10.7).
    """
    if distance_m < grid.pixel_size_m:
        return None
    return (
        f"reference end distance to the lower grid boundary: {distance_m} m "
        f"(not below the pixel size {grid.pixel_size_m} m)"
    )


def blocked_share_text(blocked_info):
    """Limitation item for the blocked-cell share, formatted from the computed values."""
    if blocked_info["share"] is None:
        return "no reference point lies inside the grid, so no blocked-cell share is available"
    return (
        f"{blocked_info['blocked']} of {blocked_info['inside']} reference points "
        f"({blocked_info['percent']:.2f}%) lie in cells blocked by the slope limit"
    )


def build_limitations(P, blocked_info, end_distance_m=None):
    """The 14 limitation items in the fixed order of the design.

    `end_distance_m` is accepted for the call signature of the design; the texts do not use it.
    """
    file = str(PARAMS_PATH)
    seg = require(P, "validation_route", "locked_reference_segment",
                  "recorded_not_explained", file=file)
    mmgis = require(seg, "mmgis_third_segment", file=file)
    places = require(seg, "places_third_segment", file=file)
    segment3 = SEGMENT3_TEMPLATE.format(
        first_sol=require(mmgis, "first_sol", file=file),
        last_sol=require(mmgis, "last_sol", file=file),
        places_len=require(places, "length_m_aeqd", file=file),
        mmgis_len=require(mmgis, "length_m_aeqd", file=file),
    )
    return [
        END_ON_BOTTOM_ROW_TEXT,
        segment3,
        EAST_WEST_TEXT,
        blocked_share_text(blocked_info),
        require_text(P, "slope", "confidence_layer", "value"),
        require_text(P, "cost_function", "corner_cutting", "value"),
        require_text(P, "comparison", "metrics", "end_point_error_m", "report_note"),
        require_text(P, "comparison", "reporting", "value"),
        require_text(P, "reference_path", "mmgis_latitude", "value"),
        require_text(P, "slope", "slope_limit_deg", "note"),
        LIMIT_MAX_SLOPE_PIXEL_CENTRES,
        LIMIT_CORNER_CUTTING,
        LIMIT_NO_DIST_TOTAL,
        LIMIT_SEGMENT1_LEAVES_GRID,
    ]


# ---------------------------------------------------------------------------
# Report assembly and atomic writer
# ---------------------------------------------------------------------------

# Result keys that are null when the status has no metric result (Req 7.5, 9.1).
METRIC_RESULT_KEYS = ("M0", "M1", "M2", "M3", "end_point_error_m", "verdict")


def build_report(*, run_date, run_notes, parameters, data_versions, resampling,
                 results, limitations):
    """Assemble the report dict in the block order of the design.

    `results` holds the computed result fields (status, reason, start, end, costs,
    M0..M3, end_point_error_m, verdict, caveat, blocked_reference, ...). If its status
    is not ok or snapped, M0, M1, M2, M3, end_point_error_m and verdict are set to
    None; every other block is still written. Inputs are not modified.
    """
    results = dict(results)
    if results.get("status") not in STATUSES_WITH_RESULT:
        for key in METRIC_RESULT_KEYS:
            results[key] = None
    return {
        "locked_commit": LOCKED_COMMIT,
        "run_date": run_date,
        "run_notes": list(run_notes),
        "parameters": parameters,
        "data_versions": data_versions,
        "resampling": resampling,
        "results": results,
        "limitations": list(limitations),
    }


def write_report_atomic(report, path=REPORT_PATH):
    """Write the report as UTF-8 JSON (indent 2, ensure_ascii False) atomically.

    The text goes to a temporary file in the folder of `path` (created if missing),
    then os.replace moves it onto `path`. The temporary file is removed on error.
    """
    path = Path(path)
    out_dir = path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    fd, tmp_name = tempfile.mkstemp(dir=out_dir, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Command line and entry points
# ---------------------------------------------------------------------------


def parse_args(argv):
    """Only `--note` exists: no parameter, input path or threshold can be changed."""
    parser = argparse.ArgumentParser(prog="run_validation.py")
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="text stored in run_notes (repeatable)",
    )
    return parser.parse_args(argv)



# Process exit codes (task 10.1 instruction; Requirement 11).
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_ABORT = 2


def _file_size(path):
    return os.path.getsize(path)


def _sha_checked(path):
    """SHA-256 of an input file; a missing file is an abort, not a crash."""
    try:
        return sha256_file(path)
    except OSError as exc:
        raise ValidationAbort(f"{path}: cannot read file ({exc})") from None


def _file_block(root, rel, sha=None):
    path = Path(root) / rel
    return {
        "path": rel.as_posix(),
        "sha256": sha if sha is not None else _sha_checked(path),
        "bytes": _file_size(path),
    }


def _cell_list(cell):
    return None if cell is None else [int(cell[0]), int(cell[1])]


def _end_block(cell, snap, clamped):
    return {"cell": _cell_list(cell), "snap_cells": snap, "clamped": bool(clamped)}


def _compute_metrics(route, grid, ref, P, tolerances, spacing, centre, radius, route_module):
    """Resample both lines in aeqd metres and compute M0..M3 and the end-point errors."""
    route_xy = []
    for r, c in route.path:
        e, n = cell_centre(r, c, grid, route_module)
        route_xy.append(dtm_to_aeqd(e, n, centre, radius))
    route_s = resample(route_xy, spacing)
    ref_s = resample(ref.aeqd_xy, spacing)
    d = nearest_distances(route_s, ref_s)
    zero = m0(d)
    spread = m2(d)
    total, points = dtw(route_s, ref_s)
    ends = end_point_errors(route_s, ref_s)
    note = require(P, "comparison", "metrics", "end_point_error_m", "report_note",
                   file=str(PARAMS_PATH))
    return {
        "route_samples": int(route_s.shape[0]),
        "reference_samples": int(ref_s.shape[0]),
        "M0": {"mean_m": zero["mean"], "max_m": zero["max"]},
        "M1": {
            format_tol(t): {k: v for k, v in m1(route_s, ref_s, t).items() if k != "d_tol"}
            for t in tolerances
        },
        "M2": {"median_m": spread["median"], "p95_m": spread["p95"]},
        "M3": {"dtw_per_path_point_m": total / points, "warping_path_points": int(points)},
        "end_point_error_m": {"first": ends["first_m"], "last": ends["last_m"], "note": note},
    }


def _summary_lines(report, primary_key):
    res = report["results"]
    lines = [f"status: {res['status']}"]
    if res.get("reason"):
        lines.append(f"reason: {res['reason']}")
    lines.append(f"verdict: {res['verdict']}")
    if res.get("M1") is not None:
        for key, entry in res["M1"].items():
            marker = " (primary)" if key == primary_key else ""
            lines.append(f"M1 at d_tol {key} m{marker}: {entry['M1']}")
    else:
        lines.append("M1: null")
    if res.get("M0") is not None:
        lines.append(f"M0 mean: {res['M0']['mean_m']} m, max: {res['M0']['max_m']} m")
    else:
        lines.append("M0: null")
    blocked = res["blocked_reference"]
    lines.append(
        f"blocked reference share: {blocked['blocked']} of {blocked['inside']} "
        f"({blocked['percent']} %)"
    )
    return lines


def _execute(root, argv):
    """All checks and computations, then the single report write. Returns the console lines."""
    root = Path(root)
    args = parse_args(argv)
    report_path = root / REPORT_PATH
    if report_path.exists():
        raise ValidationAbort(f"{REPORT_PATH} already exists; the validation runs once")

    file = str(PARAMS_PATH)
    P = read_json(root / PARAMS_PATH)
    check_lock(P)

    grid = load_grid_strict(root / GRID_PATH)
    slope = load_slope_strict(root / SLOPE_PATH)
    hashes = {
        "slope": _sha_checked(root / SLOPE_PATH),
        "grid": _sha_checked(root / GRID_PATH),
        "places": _sha_checked(root / PLACES_PATH),
    }
    hash_record = check_hashes(P, hashes)
    check_slope_shape(slope, grid)

    d_primary = require(P, "tolerance", "d_tol_primary_m", "value", file=file)
    d_sens = require(P, "tolerance", "d_tol_sensitivity_m", "value", file=file)
    thresholds = require(P, "tolerance", "verdict_thresholds_M1", file=file)
    tolerances = [d_primary] + list(d_sens)
    check_floor_rule(d_primary, grid.pixel_size_m)

    route_module = load_route_module(root)
    cost_params, _raw = load_router_config(route_module, root / ROUTER_CONFIG_PATH)
    check_config_matches(cost_params, P)

    r_snap = require(P, "validation_route", "snap", "r_snap_cells", file=file)
    spacing = require(P, "comparison", "line_resampling", "spacing_m", file=file)
    radius = require(P, "coordinate_system", "crs_check", "radius_m", file=file)
    centre_d = require(P, "coordinate_system", "distance_projection", "centre", file=file)
    centre = (require(centre_d, "lat_deg", file=file), require(centre_d, "lon_deg", file=file))
    segment = require(P, "validation_route", "locked_reference_segment", "segment_used", file=file)

    rows = read_places_rows(root / PLACES_PATH)
    rover_sols = [int(r["sol"]) for r in rows if r["frame"] == FRAME_ROVER]
    check_rover_sol_order(rover_sols)
    ref = build_reference(rows, P, grid)

    cost = build_route_cost(route_module, slope, cost_params)
    s_row, s_col, s_clamped = point_to_cell(*ref.dtm_en[0], grid)
    e_row, e_col, e_clamped = point_to_cell(*ref.dtm_en[-1], grid)
    route = run_route(
        cost, (s_row, s_col), (e_row, e_col), cost_params, r_snap,
        route_module=route_module, grid=grid, centre=centre, radius_m=radius,
        start_clamped=s_clamped, end_clamped=e_clamped,
    )
    route = gate(route, cost, r_snap)

    metrics = None
    if route.status in STATUSES_WITH_RESULT:
        metrics = _compute_metrics(route, grid, ref, P, tolerances, spacing, centre,
                                   radius, route_module)
    blocked_info = blocked_share(ref.dtm_en, cost, grid, slope)

    primary_key = format_tol(d_primary)
    m1_primary = metrics["M1"][primary_key]["M1"] if metrics else None
    vblock = verdict_block(route.status, m1_primary, thresholds, P)

    end_distance = end_distance_to_lower_boundary(ref.dtm_en[-1], grid)
    run_notes = list(args.note)
    distance_note = end_distance_run_note(end_distance, grid)
    if distance_note is not None:
        run_notes.append(distance_note)
    limitations = build_limitations(P, blocked_info, end_distance)

    sol_values = [int(r["sol"]) for r in rows if r["frame"] == FRAME_ROVER]
    data_versions = {
        "places": {
            **_file_block(root, PLACES_PATH, hash_record["places"]["sha256"]),
            "locked_sha256": hash_record["places"]["locked_sha256"],
            "match": hash_record["places"]["match"],
            "release": require(P, "reference_path", "authoritative_citation", "value", file=file),
            "sol_range": [min(sol_values), max(sol_values)] if sol_values else None,
        },
        "grid": {
            **_file_block(root, GRID_PATH, hash_record["grid"]["sha256"]),
            "locked_sha256": hash_record["grid"]["locked_sha256"],
            "match": hash_record["grid"]["match"],
        },
        "slope": {
            **_file_block(root, SLOPE_PATH, hash_record["slope"]["sha256"]),
            "locked_sha256": hash_record["slope"]["locked_sha256"],
            "match": hash_record["slope"]["match"],
        },
        "params": _file_block(root, PARAMS_PATH),
        "router_config": _file_block(root, ROUTER_CONFIG_PATH),
        "terrain": {
            "name": require(P, "coordinate_system", "terrain_file", "source_product",
                            "value", file=file),
            "version": require(P, "coordinate_system", "terrain_file", "version",
                               "value", file=file),
        },
    }
    parameters = {
        "params_file": {"path": PARAMS_PATH.as_posix(),
                        "sha256": data_versions["params"]["sha256"]},
        "slope_limit_deg": cost_params.slope_limit_deg,
        "cost_base": cost_params.cost_base,
        "cost_coefficient": cost_params.cost_coefficient,
        "cost_exponent": cost_params.cost_exponent,
        "connectivity": cost_params.connectivity,
        "r_snap_cells": r_snap,
        "resampling_spacing_m": spacing,
        "d_tol_primary_m": d_primary,
        "d_tol_sensitivity_m": list(d_sens),
        "verdict_thresholds_M1": thresholds,
        "projection": {
            "radius_m": radius,
            "aeqd_centre": {"lat_deg": centre[0], "lon_deg": centre[1]},
        },
        "reference_indices": {
            "from": require(segment, "path_index_from", file=file),
            "to": require(segment, "path_index_to", file=file),
            "points": require(segment, "points", file=file),
        },
    }
    resampling = {
        "method": require(P, "comparison", "line_resampling", "value", file=file),
        "spacing_m": spacing,
        "route_samples": metrics["route_samples"] if metrics else None,
        "reference_samples": metrics["reference_samples"] if metrics else None,
    }
    results = {
        "status": route.status,
        "reason": route.reason,
        "start": _end_block(route.start_cell, route.start_snap_cells, route.start_clamped),
        "end": _end_block(route.end_cell, route.end_snap_cells, route.end_clamped),
        "route_cost_find_path": route.find_path_cost,
        "route_cost_recomputed": route.recomputed_cost,
        "route_length_m": route.length_m,
        "M0": metrics["M0"] if metrics else None,
        "M1": metrics["M1"] if metrics else None,
        "M2": metrics["M2"] if metrics else None,
        "M3": metrics["M3"] if metrics else None,
        "end_point_error_m": metrics["end_point_error_m"] if metrics else None,
        "verdict": vblock["verdict"],
        "caveat": vblock["caveat"],
        "blocked_reference": blocked_info,
        "reference_end_distance_to_lower_boundary_m": end_distance,
    }
    report = build_report(
        run_date=datetime.date.today().isoformat(),
        run_notes=run_notes,
        parameters=parameters,
        data_versions=data_versions,
        resampling=resampling,
        results=results,
        limitations=limitations,
    )

    write_report_atomic(report, report_path)  # the only write; nothing was printed before

    lines = _summary_lines(report, primary_key)
    lines.append(f"{REPORT_PATH.as_posix()} {_file_size(report_path)}")  # file lines come last
    return lines


def run(root, argv):
    """Run the validation under the repository root `root`. Returns the exit code.

    0: a report was written (any status). 2: ValidationAbort, message on standard error.
    1: any other exception, traceback on standard error. No file is written on 1 or 2.
    Standard output is used only after the report is written.
    """
    try:
        lines = _execute(root, argv)
    except ValidationAbort as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ABORT
    except Exception:  # noqa: BLE001 - every other failure is exit code 1
        traceback.print_exc()
        return EXIT_ERROR
    for line in lines:
        print(line)
    return EXIT_OK


def main(argv=None):
    """Command-line entry: runs on the repository that contains this script."""
    if argv is None:
        argv = sys.argv[1:]
    return run(Path(__file__).resolve().parent.parent, argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
