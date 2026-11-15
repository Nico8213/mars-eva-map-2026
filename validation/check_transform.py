"""Read-only checks of the lon/lat to DTM grid transform (Perseverance data).

Check A: where the landing waypoint falls on the grid.
Check B: distance between the sphere and ellipsoid projections.
Check C: share of traverse vertices in blocked slope cells.

Only numpy and the Python standard library are used. Inputs are opened for
reading only.
"""

from __future__ import annotations

import datetime
import json
import math
import os
import sys
from dataclasses import dataclass

import numpy as np

# Sphere radius in metres. Source: spec section 4.3 of docs/research/nico-routing-spec.md
# and the USGS label of the HiRISE DTM (USGS_LABEL_URL).
MARS_SPHERE_RADIUS_M = 3396190.0
# Semi-major axis of the IAU oblate ellipsoid in metres, used only in Check B.
# Source: grid.json coordinate_notes (+a=3396190).
MARS_ELLIPSOID_A_M = 3396190.0
# Polar semi-axis of the IAU oblate ellipsoid in metres. Documented only: the eqc
# formula with lat_ts 0 uses a, not b, so this constant does not enter any formula.
# Source: grid.json coordinate_notes (+b=3376200).
MARS_ELLIPSOID_B_M = 3376200.0
# Blocked-share warning threshold in percent. Source: assumption of owner B in
# requirements.md (display threshold only).
BLOCKED_SHARE_WARN_PCT = 10.0
# Expected landing sol. Source: spec section 4.4.
EXPECTED_LANDING_SOL = 0
# Number of traverse vertices used in Check B. Source: Requirement 3.1.
CHECK_B_VERTEX_COUNT = 10
# USGS label URL, spec section 4.3 (the URL from the requirements Glossary entry USGS_Label).
USGS_LABEL_URL = "https://astrogeology.usgs.gov/ckan/dataset/381ba037-d8a9-4cea-86be-374e4951afe3/resource/bd39aeaf-231d-4732-b333-7636bce607ff/download/jez_hirise_soc_006_dtm_molatopography_deltageoid_1m_eqc_latts0_lon0_blend40.lbl"
# Projection formula text recorded in the results file (documentation only).
PROJECTION_FORMULA = "easting = R * radians(lon); northing = R * radians(lat); lat_ts = 0; lon_0 = 0"

# Default paths (relative to the repository root).
GRID_PATH = "data/processed/grid.json"
SLOPE_PATH = "data/processed/slope.npy"
ROUTER_CONFIG_PATH = "routing/config.json"
WAYPOINTS_PATH = "validation/data/M20_waypoints.json"
TRAVERSE_PATH = "validation/data/M20_traverse.json"
RESULTS_PATH = "validation/out/check_transform.json"
SNAPSHOT_NOTE_PATH = "validation/data/SNAPSHOT.md"

# The only grid.json fields the script reads. top_left_coordinate and
# coordinate_notes are never read (see design: they use a different figure).
GRID_FIELDS = ("top_left_x_m", "top_left_y_m", "pixel_size_m", "width", "height")


class InputError(Exception):
    """An input file is missing, unparsable, or has missing/invalid content.

    problem is one of: "missing", "unparsable", "missing_field", "invalid_value".
    """

    def __init__(self, path: str, problem: str, field: str | None = None):
        self.path = path
        self.problem = problem
        self.field = field
        text = f"{path}: {problem}"
        if field:
            text += f" {field}"
        super().__init__(text)


@dataclass(frozen=True)
class Grid:
    top_left_x_m: float
    top_left_y_m: float
    pixel_size_m: float
    width: int
    height: int


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise InputError(path, "missing") from None
    except (OSError, ValueError):
        # ValueError covers json.JSONDecodeError and UnicodeDecodeError.
        raise InputError(path, "unparsable") from None


def _coord(value) -> float:
    """Return a float for a numeric coordinate, NaN otherwise (flagged later as invalid)."""
    return float(value) if _is_number(value) else float("nan")


def load_grid(path: str) -> Grid:
    data = _read_json(path)
    if not isinstance(data, dict):
        raise InputError(path, "unparsable")
    missing = [name for name in GRID_FIELDS if name not in data]
    if missing:
        raise InputError(path, "missing_field", ", ".join(missing))
    for name in ("top_left_x_m", "top_left_y_m"):
        value = data[name]
        if not _is_number(value) or not math.isfinite(value):
            raise InputError(path, "invalid_value", name)
    pixel = data["pixel_size_m"]
    if not _is_number(pixel) or not math.isfinite(pixel) or pixel <= 0:
        raise InputError(path, "invalid_value", "pixel_size_m")
    for name in ("width", "height"):
        value = data[name]
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise InputError(path, "invalid_value", name)
    return Grid(
        top_left_x_m=float(data["top_left_x_m"]),
        top_left_y_m=float(data["top_left_y_m"]),
        pixel_size_m=float(pixel),
        width=data["width"],
        height=data["height"],
    )


def load_waypoints(path: str) -> list[dict]:
    data = _read_json(path)
    features = data.get("features") if isinstance(data, dict) else None
    if not isinstance(features, list):
        raise InputError(path, "unparsable", "features")
    if not features:
        raise InputError(path, "invalid_value", "features")
    waypoints: list[dict] = []
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            continue
        geometry = feature.get("geometry")
        properties = feature.get("properties")
        if not isinstance(geometry, dict) or geometry.get("type") != "Point":
            continue
        if not isinstance(properties, dict) or not _is_number(properties.get("sol")):
            continue
        coords = geometry.get("coordinates")
        if not isinstance(coords, (list, tuple)) or len(coords) < 2:
            continue
        waypoints.append(
            {
                "index": index,
                "sol": properties["sol"],
                "lon": _coord(coords[0]),
                "lat": _coord(coords[1]),
            }
        )
    if not waypoints:
        raise InputError(path, "invalid_value", "usable feature")
    return waypoints


def load_traverse(path: str) -> list[tuple[float, float]]:
    data = _read_json(path)
    features = data.get("features") if isinstance(data, dict) else None
    if not isinstance(features, list):
        raise InputError(path, "unparsable", "features")
    vertices: list[tuple[float, float]] = []
    for feature in features:
        geometry = feature.get("geometry") if isinstance(feature, dict) else None
        if not isinstance(geometry, dict):
            continue
        kind = geometry.get("type")
        coords = geometry.get("coordinates")
        if kind == "LineString":
            lines = [coords]
        elif kind == "MultiLineString":
            lines = coords
        else:
            continue
        if not isinstance(lines, list):
            continue
        for line in lines:
            if not isinstance(line, list):
                continue
            for point in line:
                if isinstance(point, (list, tuple)) and len(point) >= 2:
                    vertices.append((_coord(point[0]), _coord(point[1])))
    if not vertices:
        raise InputError(path, "invalid_value", "vertices")
    return vertices


def load_slope_limit(path: str) -> float:
    data = _read_json(path)
    block = data.get("slope_limit_deg") if isinstance(data, dict) else None
    value = block.get("value") if isinstance(block, dict) else None
    if not _is_number(value) or not math.isfinite(value):
        raise InputError(path, "missing_field", "slope_limit_deg.value")
    return float(value)


def load_slope_raster(path: str, grid: Grid) -> np.ndarray:
    try:
        slope = np.load(path, allow_pickle=False)
    except FileNotFoundError:
        raise InputError(path, "missing") from None
    except (OSError, ValueError, EOFError):
        raise InputError(path, "unparsable") from None
    expected = (grid.height, grid.width)
    if slope.shape != expected:
        raise InputError(
            path,
            "invalid_value",
            f"shape {tuple(slope.shape)} differs from grid (height, width) {expected}",
        )
    return slope


def lonlat_is_valid(lon: float, lat: float) -> bool:
    """True if both values are finite, -180 <= lon <= 360 and -90 <= lat <= 90."""
    try:
        lon = float(lon)
        lat = float(lat)
    except (TypeError, ValueError):
        return False
    if not (math.isfinite(lon) and math.isfinite(lat)):
        return False
    return -180.0 <= lon <= 360.0 and -90.0 <= lat <= 90.0


def project_eqc(lon_deg: float, lat_deg: float, radius_m: float) -> tuple[float, float]:
    """Equirectangular projection (lat_ts 0, lon_0 0): returns (easting, northing)."""
    return (radius_m * math.radians(lon_deg), radius_m * math.radians(lat_deg))


def project_sphere(lon_deg: float, lat_deg: float) -> tuple[float, float]:
    """Sphere_Projection: radius MARS_SPHERE_RADIUS_M."""
    return project_eqc(lon_deg, lat_deg, MARS_SPHERE_RADIUS_M)


def project_ellipsoid(lon_deg: float, lat_deg: float) -> tuple[float, float]:
    """Ellipsoid_Projection: semi-major axis MARS_ELLIPSOID_A_M.

    MARS_ELLIPSOID_B_M is not used (lat_ts 0 formula depends only on a).
    """
    return project_eqc(lon_deg, lat_deg, MARS_ELLIPSOID_A_M)


def to_pixel(grid: Grid, easting: float, northing: float) -> tuple[float, float]:
    """Unrounded, unclamped pixel position (x to the right, y downward)."""
    x = (easting - grid.top_left_x_m) / grid.pixel_size_m
    y = (grid.top_left_y_m - northing) / grid.pixel_size_m
    return (x, y)


def is_inside_grid(grid: Grid, x: float, y: float) -> bool:
    """True if 0 <= x < width and 0 <= y < height."""
    return 0 <= x < grid.width and 0 <= y < grid.height


def is_blocked(value: float, slope_limit_deg: float) -> bool:
    """Blocked if the slope is NaN or above the limit; equal to the limit is not blocked."""
    return bool(math.isnan(value) or value > slope_limit_deg)


def select_landing_waypoint(waypoints: list[dict]) -> tuple[dict, int]:
    """Waypoint with the smallest sol (lowest index on ties) and the tied count."""
    if not waypoints:
        raise ValueError("waypoints must not be empty")
    best = min(waypoints, key=lambda wp: (wp["sol"], wp["index"]))
    tied = sum(1 for wp in waypoints if wp["sol"] == best["sol"])
    return best, tied


def check_a_landing_waypoint(grid: Grid, waypoints: list[dict], warnings: list[str]) -> dict:
    """Check A: pixel position of the landing waypoint (Sphere_Projection).

    Returns a dict with an "errors" list. Waypoints with invalid lon/lat are
    recorded as errors and skipped; the remaining waypoints are still used.
    """
    errors: list[str] = []
    valid: list[dict] = []
    for wp in waypoints:
        if lonlat_is_valid(wp["lon"], wp["lat"]):
            valid.append(wp)
        else:
            errors.append(
                f"waypoint {wp['index']}: invalid lon/lat (lon={wp['lon']}, lat={wp['lat']})"
            )
    result: dict = {"errors": errors}
    if not valid:
        return result

    landing, tied = select_landing_waypoint(valid)
    easting, northing = project_sphere(landing["lon"], landing["lat"])
    x, y = to_pixel(grid, easting, northing)
    inside = is_inside_grid(grid, x, y)
    sol = landing["sol"]

    result.update(
        {
            "landing_sol": sol,
            "feature_index": landing["index"],
            "lon_deg": round(landing["lon"], 5),
            "lat_deg": round(landing["lat"], 5),
            "pixel_x": round(x, 2),
            "pixel_y": round(y, 2),
            "grid_width": grid.width,
            "grid_height": grid.height,
            "inside_grid": inside,
            "tied_count": tied,
        }
    )

    if sol != EXPECTED_LANDING_SOL:
        warnings.append(
            f"WARNING: landing waypoint has sol {sol}, but spec section 4.4 expects "
            f"sol {EXPECTED_LANDING_SOL}; {SNAPSHOT_NOTE_PATH} records start sol 13"
        )
    if not inside:
        warnings.append(
            f"WARNING: landing waypoint is outside the grid: Pixel_Position "
            f"(x={x:.2f}, y={y:.2f}), grid size {grid.width} x {grid.height}"
        )
    if tied > 1:
        warnings.append(
            f"WARNING: {tied} waypoints share the smallest sol {sol}; "
            f"using the one with the lowest index ({landing['index']})"
        )
    return result


def select_check_b_vertices(
    vertices: list[tuple[float, float]],
) -> list[tuple[int, float, float]]:
    """First min(CHECK_B_VERTEX_COUNT, n) vertices as (index, lon, lat), in file order."""
    count = min(CHECK_B_VERTEX_COUNT, len(vertices))
    return [(i, vertices[i][0], vertices[i][1]) for i in range(count)]


def check_b_sphere_vs_ellipsoid(
    vertices: list[tuple[float, float]], warnings: list[str]
) -> dict:
    """Check B: distance between Sphere_Projection and Ellipsoid_Projection.

    Distances are reported as computed; no other radius is tried. Invalid
    vertices (non-finite, lon outside -180..180, lat outside -90..90) are
    excluded with a warning that names the vertex index.
    """
    selected = select_check_b_vertices(vertices)
    count = len(selected)
    result: dict = {
        "vertex_count_used": 0,
        "distances_m": [],
        "max_distance_m": None,
        "excluded_vertices": [],
    }
    if count == 0:
        warnings.append(
            "WARNING: traverse has 0 vertices; Check B distances are skipped"
        )
        return result
    if count < CHECK_B_VERTEX_COUNT:
        warnings.append(
            f"WARNING: traverse has only {count} vertices (fewer than "
            f"{CHECK_B_VERTEX_COUNT}); Check B uses all {count}"
        )

    distances: list[dict] = []
    excluded: list[int] = []
    max_raw: float | None = None
    for index, lon, lat in selected:
        if not (lonlat_is_valid(lon, lat) and -180.0 <= float(lon) <= 180.0):
            excluded.append(index)
            warnings.append(
                f"WARNING: Check B excludes vertex {index}: invalid lon/lat "
                f"(lon={lon}, lat={lat})"
            )
            continue
        sx, sy = project_sphere(lon, lat)
        ex, ey = project_ellipsoid(lon, lat)
        raw = math.hypot(ex - sx, ey - sy)
        distances.append({"vertex_index": index, "distance_m": round(raw, 3)})
        if max_raw is None or raw > max_raw:
            max_raw = raw

    result["vertex_count_used"] = len(distances)
    result["distances_m"] = distances
    result["max_distance_m"] = round(max_raw, 3) if max_raw is not None else None
    result["excluded_vertices"] = excluded
    return result


def check_c_blocked_share(
    grid: Grid,
    vertices: list[tuple[float, float]],
    slope: np.ndarray,
    slope_limit: float,
    config_path: str,
    warnings: list[str],
) -> dict:
    """Check C: share of traverse vertices inside the grid that lie in blocked cells.

    Every vertex is converted with project_sphere and to_pixel. Vertices that are
    not finite or not valid lon/lat count as outside the grid. The containing cell
    is slope[floor(y), floor(x)]. Returns a dict with an "errors" list; on a bad
    input (slope shape, Router_Config value, no vertices) no vertex is counted.
    """
    errors: list[str] = []
    expected = (grid.height, grid.width)
    if getattr(slope, "shape", None) != expected:
        errors.append(
            f"slope raster shape {getattr(slope, 'shape', None)} differs from grid "
            f"(height, width) {expected}"
        )
    if not _is_number(slope_limit) or not math.isfinite(slope_limit):
        errors.append(f"{config_path}: missing_field slope_limit_deg.value")
    if not vertices:
        errors.append("traverse has 0 vertices")

    result: dict = {
        "errors": errors,
        "slope_limit_deg": slope_limit if _is_number(slope_limit) else None,
        "router_config": config_path,
        "vertices_total": len(vertices),
        "inside_grid": 0,
        "outside_grid": 0,
        "blocked": 0,
        "blocked_share_pct": "n/a",
    }
    if errors:
        return result

    limit = float(slope_limit)
    print(f"Check C: slope limit {limit} degrees (from {config_path})")

    inside = 0
    outside = 0
    blocked = 0
    for lon, lat in vertices:
        if not lonlat_is_valid(lon, lat):
            outside += 1
            continue
        easting, northing = project_sphere(lon, lat)
        x, y = to_pixel(grid, easting, northing)
        if not (math.isfinite(x) and math.isfinite(y)) or not is_inside_grid(grid, x, y):
            outside += 1
            continue
        inside += 1
        if is_blocked(float(slope[math.floor(y), math.floor(x)]), limit):
            blocked += 1

    result["inside_grid"] = inside
    result["outside_grid"] = outside
    result["blocked"] = blocked

    if inside > 0:
        share = round(blocked / inside * 100, 1)
        result["blocked_share_pct"] = share
        if blocked * 100 >= BLOCKED_SHARE_WARN_PCT * inside:
            warnings.append(
                f"WARNING: {share}% of traverse vertices inside the grid are in blocked "
                f"cells (slope limit {limit} degrees)"
            )
    else:
        warnings.append(
            "WARNING: no traverse vertex is inside the grid; blocked share is n/a"
        )
    if outside > 0:
        warnings.append(
            f"WARNING: {outside} of {len(vertices)} traverse vertices are outside the grid"
        )
    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def projection_info() -> dict:
    """Projection block of the results file (constants only, no file is read)."""
    return {
        "usgs_label_url": USGS_LABEL_URL,
        "sphere_radius_m": MARS_SPHERE_RADIUS_M,
        "flattening": 0,
        "latitude_type": "planetocentric",
        "longitude_direction": "positive_east",
        "projection": "equirectangular",
        "lat_ts": 0,
        "lon_0": 0,
        "formula": PROJECTION_FORMULA,
        "ellipsoid_a_m": MARS_ELLIPSOID_A_M,
        "ellipsoid_b_m": MARS_ELLIPSOID_B_M,
        "ellipsoid_b_used_in_formula": False,
    }


def print_projection_header() -> None:
    print(f"Projection source (USGS label): {USGS_LABEL_URL}")
    print(f"Sphere radius: {MARS_SPHERE_RADIUS_M} m")
    print("Flattening: 0")
    print("Latitude type: planetocentric")
    print("Longitude direction: positive east")
    print("Projection: equirectangular")
    print("lat_ts: 0")
    print("lon_0: 0")


def print_check_a(result: dict) -> None:
    if "landing_sol" not in result:
        return
    print(
        f"Check A: landing waypoint sol {result['landing_sol']} "
        f"(feature {result['feature_index']}), "
        f"lon {result['lon_deg']:.5f}, lat {result['lat_deg']:.5f}"
    )
    print(
        f"Check A: Pixel_Position x={result['pixel_x']:.2f}, y={result['pixel_y']:.2f} "
        f"on grid {result['grid_width']} x {result['grid_height']}, "
        f"inside grid: {result['inside_grid']}"
    )


def print_check_b(result: dict) -> None:
    for item in result["distances_m"]:
        print(f"Check B: vertex {item['vertex_index']} distance {item['distance_m']:.3f} m")
    if result["max_distance_m"] is not None:
        print(f"Check B: maximum distance {result['max_distance_m']:.3f} m")


def print_check_c(result: dict) -> None:
    print(
        f"Check C: vertices {result['vertices_total']}, inside grid {result['inside_grid']}, "
        f"outside grid {result['outside_grid']}, blocked {result['blocked']}, "
        f"blocked share {result['blocked_share_pct']}"
    )


def _strip_errors(result: dict) -> dict:
    return {key: value for key, value in result.items() if key != "errors"}


def build_results(
    projection: dict,
    a: dict,
    b: dict,
    c: dict,
    warnings: list[str],
    inputs: dict[str, str],
    run_date: str,
) -> dict:
    """Results document with the key order of the design."""
    return {
        "run_date": run_date,
        "inputs": dict(inputs),
        "projection": dict(projection),
        "check_a": _strip_errors(a),
        "check_b": _strip_errors(b),
        "check_c": _strip_errors(c),
        "warnings": list(warnings),
    }


def write_results(results: dict, path: str) -> int:
    """Write the results as JSON and return the on-disk size in bytes.

    Raises OSError if the directory or file cannot be written.
    """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, ensure_ascii=False, sort_keys=False)
        handle.write("\n")
    return os.stat(path).st_size


def _default_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _format_error(error: InputError) -> str:
    return f"ERROR: {error}"


def main(argv: list[str] | None = None) -> int:
    """Run checks A, B, C. Optional argument: --root DIR (default: repository root)."""
    args = list(argv) if argv is not None else []
    root = _default_root()
    if args[:1] == ["--root"] and len(args) >= 2:
        root = args[1]

    def full(rel: str) -> str:
        return os.path.join(root, rel)

    errors: list[str] = []
    warnings: list[str] = []

    grid = None
    waypoints = None
    vertices = None
    slope_limit = None
    slope = None
    zero_vertices = False

    try:
        grid = load_grid(full(GRID_PATH))
    except InputError as exc:
        errors.append(_format_error(exc))
    try:
        waypoints = load_waypoints(full(WAYPOINTS_PATH))
    except InputError as exc:
        errors.append(_format_error(exc))
    try:
        vertices = load_traverse(full(TRAVERSE_PATH))
    except InputError as exc:
        errors.append(_format_error(exc))
        if exc.problem == "invalid_value" and exc.field == "vertices":
            zero_vertices = True
    try:
        slope_limit = load_slope_limit(full(ROUTER_CONFIG_PATH))
    except InputError as exc:
        errors.append(_format_error(exc))
    if grid is not None:
        try:
            slope = load_slope_raster(full(SLOPE_PATH), grid)
        except InputError as exc:
            errors.append(_format_error(exc))

    print_projection_header()

    check_a: dict = {"errors": []}
    check_b: dict = {
        "vertex_count_used": 0,
        "distances_m": [],
        "max_distance_m": None,
        "excluded_vertices": [],
    }
    check_c: dict = {"errors": []}

    if grid is not None and waypoints is not None:
        check_a = check_a_landing_waypoint(grid, waypoints, warnings)
        for message in check_a["errors"]:
            errors.append(f"ERROR: {WAYPOINTS_PATH}: {message}")
        print_check_a(check_a)

    if vertices is not None or zero_vertices:
        check_b = check_b_sphere_vs_ellipsoid(vertices or [], warnings)
        print_check_b(check_b)

    if (
        grid is not None
        and vertices is not None
        and slope is not None
        and slope_limit is not None
    ):
        check_c = check_c_blocked_share(
            grid, vertices, slope, slope_limit, ROUTER_CONFIG_PATH, warnings
        )
        for message in check_c["errors"]:
            errors.append(f"ERROR: {message}")
        if not check_c["errors"]:
            print_check_c(check_c)

    for warning in warnings:
        print(warning)

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1

    inputs = {
        "grid": GRID_PATH,
        "slope": SLOPE_PATH,
        "router_config": ROUTER_CONFIG_PATH,
        "waypoints": WAYPOINTS_PATH,
        "traverse": TRAVERSE_PATH,
    }
    results = build_results(
        projection_info(),
        check_a,
        check_b,
        check_c,
        warnings,
        inputs,
        datetime.date.today().isoformat(),
    )
    target = full(RESULTS_PATH)
    try:
        size = write_results(results, target)
    except OSError as exc:
        print(f"ERROR: {RESULTS_PATH} {exc.strerror or exc}", file=sys.stderr)
        return 1
    print(f"{RESULTS_PATH} {size}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
