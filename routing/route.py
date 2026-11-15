"""Least-cost route tool (role B). Core types and config loading."""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "routing" / "out"
MAX_BYTES = 52_428_800

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_REQUIRED_KEYS = (
    "cost_function",
    "slope_limit_deg",
    "cost_base",
    "cost_coefficient",
    "cost_exponent",
    "connectivity",
)
_NUMERIC_KEYS = ("slope_limit_deg", "cost_base", "cost_coefficient", "cost_exponent")


class RoutingError(Exception):
    """Error with a message and a process exit code (1 unreachable, 2 invalid input)."""

    def __init__(self, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class CostParams:
    slope_limit_deg: float
    cost_base: float
    cost_coefficient: float
    cost_exponent: float
    connectivity: int  # 4 or 8


@dataclass(frozen=True)
class Grid:
    pixel_size_m: float
    width: int | None  # None when grid.json omits it; filled from the slope shape
    height: int | None
    easting_m: float  # top-left corner easting (top_left_x_m or top_left.easting_m)
    northing_m: float  # top-left corner northing (top_left_y_m or top_left.northing_m)
    crs: str
    nodata_value: float | None = None  # explicit nodata declared by grid.json, if any


def _has_valid_date(basis: str) -> bool:
    for m in _DATE_RE.finditer(basis):
        try:
            datetime.date.fromisoformat(m.group(0))
            return True
        except ValueError:
            continue
    return False


def load_config(path: Path) -> tuple[CostParams, dict]:
    """Return validated cost parameters and the raw config dict.

    Raises RoutingError (exit code 2) naming the file, key and rejected value.
    """
    path = Path(path)

    def fail(key: str | None, detail: str, value: object = None) -> RoutingError:
        parts = [f"config file {path}"]
        if key is not None:
            parts.append(f"key '{key}'")
        msg = ": ".join(parts) + f": {detail}"
        if value is not None:
            msg += f" (rejected value: {value!r})"
        return RoutingError(msg, 2)

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise fail(None, "file not found") from None
    except (OSError, UnicodeDecodeError) as exc:
        raise fail(None, f"cannot read file ({exc})") from None
    try:
        raw = json.loads(text)
    except ValueError as exc:
        raise fail(None, f"malformed JSON ({exc})") from None
    if not isinstance(raw, dict):
        raise fail(None, "malformed config, top level must be an object", raw)

    for key in _REQUIRED_KEYS:
        if key not in raw:
            raise fail(key, "required key is missing")
        entry = raw[key]
        if not isinstance(entry, dict):
            raise fail(key, "entry must be an object with 'value' and 'basis'", entry)
        value = entry.get("value")
        if value is None or (isinstance(value, str) and not value.strip()):
            raise fail(key, "'value' is missing or empty", value)
        basis = entry.get("basis")
        if not isinstance(basis, str) or not basis.strip():
            raise fail(key, "'basis' is missing or empty", basis)
        if not _has_valid_date(basis):
            raise fail(key, "'basis' must contain a valid YYYY-MM-DD date", basis)

    cf = raw["cost_function"]["value"]
    if cf != "quadratic_slope":
        raise fail("cost_function", "unsupported value, must be 'quadratic_slope'", cf)

    nums: dict[str, float] = {}
    for key in _NUMERIC_KEYS:
        v = raw[key]["value"]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise fail(key, "value must be a number", v)
        try:
            fv = float(v)
        except OverflowError:
            raise fail(key, "value must be finite and greater than 0", v) from None
        if not math.isfinite(fv) or fv <= 0:
            raise fail(key, "value must be finite and greater than 0", v)
        nums[key] = fv

    conn = raw["connectivity"]["value"]
    if isinstance(conn, bool) or not isinstance(conn, int) or conn not in (4, 8):
        raise fail("connectivity", "value must be the integer 4 or 8", conn)

    params = CostParams(
        slope_limit_deg=nums["slope_limit_deg"],
        cost_base=nums["cost_base"],
        cost_coefficient=nums["cost_coefficient"],
        cost_exponent=nums["cost_exponent"],
        connectivity=conn,
    )
    return params, raw


DEFAULT_PIXEL_SIZE_M = 1.0
DEFAULT_CRS = "unknown"
MAX_SLOPE_DEG = 90.0  # a slope outside [0, 90] degrees is a sentinel, not terrain
_CHUNK_ROWS = 1024


def _is_number(v: object) -> bool:
    return not isinstance(v, bool) and isinstance(v, (int, float))


def _warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def load_grid(path: Path) -> Grid:
    """Read grid.json. Missing fields get defaults and a warning on stderr.

    Real-file names are read first (top_left_x_m, top_left_y_m, crs_wkt); the older
    names (top_left.easting_m, top_left.northing_m, crs) are accepted as a fallback.
    A field that is present but has the wrong type raises RoutingError (exit code 2).
    """
    path = Path(path)

    def fail(detail: str) -> RoutingError:
        return RoutingError(f"grid file {path}: {detail}", 2)

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise fail("file not found") from None
    except (OSError, UnicodeDecodeError) as exc:
        raise fail(f"cannot read file ({exc})") from None
    try:
        raw = json.loads(text)
    except ValueError as exc:
        raise fail(f"malformed JSON ({exc})") from None
    if not isinstance(raw, dict):
        raise fail("top level must be a JSON object")

    def finite_number(key: str, v: object) -> float:
        if not _is_number(v) or not math.isfinite(v):
            raise fail(f"field '{key}' must be a finite number (rejected value: {v!r})")
        return float(v)

    # pixel size
    if "pixel_size_m" in raw:
        px = finite_number("pixel_size_m", raw["pixel_size_m"])
        if px <= 0:
            raise fail(f"field 'pixel_size_m' must be a number greater than 0 (rejected value: {px!r})")
    else:
        px = DEFAULT_PIXEL_SIZE_M
        _warn(f"grid file {path}: 'pixel_size_m' missing, using default {px}")

    # width and height (None means: take from the slope array shape)
    dims: dict[str, int | None] = {}
    for key in ("width", "height"):
        if key in raw:
            v = raw[key]
            if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
                raise fail(f"field '{key}' must be an integer greater than 0 (rejected value: {v!r})")
            dims[key] = v
        else:
            dims[key] = None
            _warn(f"grid file {path}: '{key}' missing, will use the slope array shape")

    # top-left corner
    easting: float | None = None
    northing: float | None = None
    if "top_left_x_m" in raw or "top_left_y_m" in raw:
        if "top_left_x_m" in raw:
            easting = finite_number("top_left_x_m", raw["top_left_x_m"])
        if "top_left_y_m" in raw:
            northing = finite_number("top_left_y_m", raw["top_left_y_m"])
    tl = raw.get("top_left")
    if isinstance(tl, dict):
        if easting is None and "easting_m" in tl:
            easting = finite_number("top_left.easting_m", tl["easting_m"])
        if northing is None and "northing_m" in tl:
            northing = finite_number("top_left.northing_m", tl["northing_m"])
    elif tl is not None:
        raise fail(f"field 'top_left' must be an object (rejected value: {tl!r})")
    if easting is None:
        easting = 0.0
        _warn(f"grid file {path}: top-left easting missing, using default {easting}")
    if northing is None:
        northing = (dims["height"] or 0) * px
        _warn(f"grid file {path}: top-left northing missing, using default {northing}")

    # CRS: only carried into the object, never used in the computation
    crs = DEFAULT_CRS
    for key in ("crs_wkt", "crs"):
        v = raw.get(key)
        if isinstance(v, str) and v.strip():
            crs = v
            break
    else:
        _warn(f"grid file {path}: 'crs_wkt' and 'crs' missing, using {DEFAULT_CRS!r}")

    # optional explicit nodata value
    nodata = raw.get("nodata_value")
    nodata_value = float(nodata) if _is_number(nodata) and math.isfinite(nodata) else None

    return Grid(
        pixel_size_m=px,
        width=dims["width"],
        height=dims["height"],
        easting_m=easting,
        northing_m=northing,
        crs=crs,
        nodata_value=nodata_value,
    )


def load_slope(path: Path, grid: Grid) -> np.ndarray:
    """Open slope.npy as a read-only memory map; check it is 2D and matches the grid.

    If grid.width or grid.height is None, that dimension is not checked.
    """
    path = Path(path)

    def fail(detail: str) -> RoutingError:
        return RoutingError(f"slope file {path}: {detail}", 2)

    try:
        arr = np.load(path, mmap_mode="r", allow_pickle=False)
    except FileNotFoundError:
        raise fail("file not found") from None
    except Exception as exc:  # invalid NumPy file, pickled object, unreadable
        raise fail(f"not a valid NumPy array file ({exc})") from None
    if not isinstance(arr, np.ndarray):
        raise fail("not a single NumPy array")
    if arr.ndim != 2:
        raise fail(f"slope array must have 2 dimensions, found {arr.ndim}")
    if arr.dtype.kind not in "fiu":
        raise fail(f"slope array must be numeric, found dtype {arr.dtype}")
    if (grid.height is not None and arr.shape[0] != grid.height) or (
        grid.width is not None and arr.shape[1] != grid.width
    ):
        expected = (grid.height, grid.width)
        raise fail(f"slope array shape {arr.shape} does not match grid (height, width) {expected}")
    return arr


def invalid_slope_mask(s: np.ndarray, nodata_value: float | None = None) -> np.ndarray:
    """True where a slope value is missing: NaN, inf, outside [0, 90] degrees, or the declared nodata.

    0 is a valid slope (flat ground) and is never treated as missing.
    """
    bad = ~np.isfinite(s) | (s < 0) | (s > MAX_SLOPE_DEG)
    if nodata_value is not None:
        bad |= s == nodata_value
    return bad

def build_cost_raster(
    slope: np.ndarray,
    p: CostParams,
    nodata_value: float | None = None,
    slope_removed: bool = False,
) -> np.ndarray:
    """Per-pixel traversal cost (float64). Missing slopes and slopes above the limit are np.inf.

    With slope_removed=True the slope layer is not a cost input: every cell costs cost_base
    and nothing is blocked (the slope limit and the missing-data rule both come from slope).

    Works in row chunks so a memory-mapped slope array is never converted whole.
    """
    if slope_removed:
        return np.full(slope.shape, p.cost_base, dtype=np.float64)
    cost = np.full(slope.shape, np.inf, dtype=np.float64)
    for r0 in range(0, slope.shape[0], _CHUNK_ROWS):
        s = np.asarray(slope[r0 : r0 + _CHUNK_ROWS], dtype=np.float64)
        ok = ~invalid_slope_mask(s, nodata_value) & (s <= p.slope_limit_deg)
        block = cost[r0 : r0 + _CHUNK_ROWS]
        block[ok] = p.cost_base + p.cost_coefficient * (s[ok] / p.slope_limit_deg) ** p.cost_exponent
    return cost

def coord_to_pixel(easting_m: float, northing_m: float, g: Grid) -> tuple[int, int]:
    """Map a map coordinate to (row, col). The result may lie outside the grid."""
    col = math.floor((easting_m - g.easting_m) / g.pixel_size_m)
    row = math.floor((g.northing_m - northing_m) / g.pixel_size_m)
    return int(row), int(col)


def pixel_to_coord(row: int, col: int, g: Grid) -> tuple[float, float]:
    """Return (easting_m, northing_m) of the pixel centre."""
    easting = g.easting_m + (col + 0.5) * g.pixel_size_m
    northing = g.northing_m - (row + 0.5) * g.pixel_size_m
    return easting, northing


@dataclass(frozen=True)
class EndpointSpec:
    """One endpoint as given by the user: form 'pixel' is (row, col), 'coord' is (easting, northing)."""

    form: str  # "pixel" or "coord"
    a: float  # row or easting_m
    b: float  # col or northing_m


def resolve_endpoint(label: str, spec: EndpointSpec, g: Grid) -> tuple[int, int]:
    """Return (row, col) for an endpoint. Raises RoutingError (2 invalid value, 1 outside grid)."""
    if spec.form not in ("pixel", "coord"):
        raise RoutingError(f"{label} endpoint: unknown form {spec.form!r}", 2)
    for v in (spec.a, spec.b):
        if isinstance(v, bool) or not isinstance(v, (int, float, np.integer, np.floating)):
            raise RoutingError(f"{label} endpoint: value must be a number (rejected value: {v!r})", 2)
        if not math.isfinite(v):
            raise RoutingError(f"{label} endpoint: value must be finite (rejected value: {v!r})", 2)

    if spec.form == "pixel":
        if spec.a != int(spec.a) or spec.b != int(spec.b):
            raise RoutingError(
                f"{label} endpoint: pixel row and column must be integers "
                f"(rejected value: ({spec.a!r}, {spec.b!r}))",
                2,
            )
        row, col = int(spec.a), int(spec.b)
    else:
        row, col = coord_to_pixel(float(spec.a), float(spec.b), g)

    if not (0 <= row < g.height and 0 <= col < g.width):
        raise RoutingError(
            f"{label} endpoint is outside the grid: pixel (row {row}, col {col}) "
            f"is not within {g.height} rows x {g.width} columns",
            1,
        )
    return row, col


def find_path(
    cost: np.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
    connectivity: int,
) -> tuple[list[tuple[int, int]], float]:
    """Least-cost path as ([(row, col), ...], total cost). Raises RoutingError (exit 1)."""
    blocked = [
        name for name, (r, c) in (("start", start), ("end", end)) if not np.isfinite(cost[r, c])
    ]
    if blocked:
        which = " and ".join(blocked)
        raise RoutingError(f"{which} endpoint is on a blocked cell", 1)
    if tuple(start) == tuple(end):
        return [(int(start[0]), int(start[1]))], 0.0

    from skimage.graph import route_through_array

    try:
        path, total = route_through_array(
            cost, tuple(start), tuple(end), fully_connected=(connectivity == 8), geometric=True
        )
    except ValueError:
        raise RoutingError("no path exists between start and end", 1) from None
    if not math.isfinite(total):
        raise RoutingError("no path exists between start and end", 1)
    return [(int(r), int(c)) for r, c in path], float(total)


def path_cost(cost: np.ndarray, path: list[tuple[int, int]]) -> float:
    """Sum of 0.5 * (c_i + c_j) * step_length over consecutive path cells."""
    total = 0.0
    for (r0, c0), (r1, c1) in zip(path, path[1:]):
        step = math.sqrt(2.0) if (r0 != r1 and c0 != c1) else 1.0
        total += 0.5 * (float(cost[r0, c0]) + float(cost[r1, c1])) * step
    return total


_NAME_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
_COST_FUNCTION_MAX = 500


def validate_name(name: str) -> None:
    """Accept only names matching ^[A-Za-z0-9_-]{1,64}$. Raises RoutingError (exit code 2)."""
    if not isinstance(name, str) or _NAME_RE.fullmatch(name) is None:
        raise RoutingError(
            f"invalid route name {name!r}: name must match ^[A-Za-z0-9_-]{{1,64}}$ "
            "(1 to 64 characters: letters, digits, underscore, hyphen)",
            2,
        )


def get_commit_hash() -> str:
    """Return the output of `git rev-parse HEAD`, or "unknown" on any failure."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        commit = result.stdout.strip()
        return commit if commit else "unknown"
    except Exception:
        return "unknown"


def _cost_function_text(raw_config: dict, p: CostParams, exclude: str | None = None) -> str:
    def val(key: str) -> object:
        return raw_config[key]["value"]

    params = (
        f"cost_base={val('cost_base')}, cost_coefficient={val('cost_coefficient')}, "
        f"cost_exponent={val('cost_exponent')}, slope_limit_deg={val('slope_limit_deg')}, "
        f"connectivity={val('connectivity')}, geometric=true"
    )
    text = (
        f"{val('cost_function')}: cost = cost_base + cost_coefficient * "
        f"(slope / slope_limit_deg) ^ cost_exponent; {params}"
    )
    if exclude is not None:
        if exclude in _cost_input_ids(raw_config):
            note = (
                f"layer '{exclude}' excluded: every cell costs cost_base={val('cost_base')}, "
                "no cell blocked, slope_limit_deg not applied; "
            )
        else:
            note = f"layer '{exclude}' excluded: not a cost input, no effect on routing; "
        text = note + text
    if len(text) > _COST_FUNCTION_MAX:
        text = f"{val('cost_function')}: {params}"
        if exclude is not None:
            text = f"layer '{exclude}' excluded; " + text
    return text[:_COST_FUNCTION_MAX]


def _cost_input_ids(raw_config: dict) -> list[str]:
    entry = raw_config.get("cost_inputs")
    value = entry.get("value") if isinstance(entry, dict) else None
    return list(value) if isinstance(value, list) else []


def load_layer_ids(path: Path) -> list[str]:
    """Return the layer ids (lower-case layer names) listed in layers.json. Raises RoutingError (2)."""
    path = Path(path)

    def fail(detail: str) -> RoutingError:
        return RoutingError(f"layers file {path}: {detail}", 2)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise fail("file not found") from None
    except (OSError, UnicodeDecodeError) as exc:
        raise fail(f"cannot read file ({exc})") from None
    except ValueError as exc:
        raise fail(f"malformed JSON ({exc})") from None
    if not isinstance(raw, list) or not raw:
        raise fail("top level must be a non-empty JSON array")
    ids: list[str] = []
    for item in raw:
        name = item.get("name") if isinstance(item, dict) else None
        if not isinstance(name, str) or not name.strip():
            raise fail(f"every entry needs a non-empty 'name' (rejected value: {item!r})")
        layer_id = re.sub(r"\s+", "_", name.strip().lower())
        if layer_id not in ids:
            ids.append(layer_id)
    return ids


def load_cost_inputs(raw_config: dict, config_path: Path, layer_ids: list[str]) -> list[str]:
    """Return the cost-input layer ids from config key 'cost_inputs'. Raises RoutingError (2)."""
    entry = raw_config.get("cost_inputs")
    value = entry.get("value") if isinstance(entry, dict) else None
    basis = entry.get("basis") if isinstance(entry, dict) else None
    problem = None
    if entry is None:
        problem = "required key is missing for --exclude"
    elif not isinstance(basis, str) or not _has_valid_date(basis):
        problem = "'basis' must be text with a valid YYYY-MM-DD date"
    elif not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
        problem = "'value' must be a non-empty list of layer ids"
    else:
        unknown = [v for v in value if v not in layer_ids]
        if unknown:
            problem = f"unknown layer ids {unknown!r}, valid ids are {layer_ids!r}"
    if problem is not None:
        raise RoutingError(f"config file {config_path}: key 'cost_inputs': {problem}", 2)
    return list(value)


def build_feature(
    name: str,
    path: list[tuple[int, int]],
    slope: np.ndarray,
    g: Grid,
    p: CostParams,
    raw_config: dict,
    start_poi: str | None,
    end_poi: str | None,
    commit: str,
    data_used: list[str] | None = None,
    exclude: str | None = None,
    nodata_value: float | None = None,
) -> dict:
    """Build the GeoJSON Feature for a route. Contains no validation metric."""
    coords = [list(pixel_to_coord(r, c, g)) for r, c in path]
    length = 0.0
    for (e0, n0), (e1, n1) in zip(coords, coords[1:]):
        length += math.hypot(e1 - e0, n1 - n0)
    values = np.array([float(slope[r, c]) for r, c in path], dtype=np.float64)
    values = values[~invalid_slope_mask(values, nodata_value)]
    if values.size == 0:
        raise RoutingError("no route cell has a valid slope value, cannot compute max_slope_deg", 2)
    max_slope = float(values.max())
    config_min = json.dumps(raw_config, separators=(",", ":"), ensure_ascii=False)
    generated = f"commit={commit}; config={config_min}"
    if exclude is not None:
        generated = f"commit={commit}; exclude={exclude}; config={config_min}"
    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": {
            "name": name,
            "start_poi": start_poi,
            "end_poi": end_poi,
            "length_m": round(length, 2),
            "max_slope_deg": round(max_slope, 2),
            "slope_threshold_deg": raw_config["slope_limit_deg"]["value"],
            "data_used": ["slope"] if data_used is None else data_used,
            "cost_function": _cost_function_text(raw_config, p, exclude),
            "generated_from": generated,
        },
    }


def write_route(feature: dict, name: str) -> Path:
    """Write routing/out/route_<name>.geojson atomically. Raises RoutingError (exit code 2)."""
    target = OUT_DIR / f"route_{name}.geojson"
    tmp_name: str | None = None
    try:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        data = json.dumps(feature, indent=2, ensure_ascii=False).encode("utf-8")
        with tempfile.NamedTemporaryFile(
            dir=OUT_DIR, prefix=f".route_{name}.", suffix=".tmp", delete=False
        ) as fh:
            tmp_name = fh.name
            fh.write(data)
        size = os.path.getsize(tmp_name)
        if size >= MAX_BYTES:
            raise RoutingError(
                f"route file {target}: size {size} bytes reaches the limit of {MAX_BYTES} bytes",
                2,
            )
        os.replace(tmp_name, target)
        tmp_name = None
    except RoutingError:
        raise
    except (OSError, ValueError) as exc:
        raise RoutingError(f"cannot write route file {target}: {exc}", 2) from None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
    return target


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="route.py",
        description="Least-cost route over a slope raster. Writes routing/out/route_<name>.geojson.",
    )
    parser.add_argument("--name", required=True, help="route name, ^[A-Za-z0-9_-]{1,64}$")
    start = parser.add_mutually_exclusive_group(required=True)
    start.add_argument("--start-rc", nargs=2, type=int, metavar=("ROW", "COL"))
    start.add_argument("--start-en", nargs=2, type=float, metavar=("EASTING", "NORTHING"))
    end = parser.add_mutually_exclusive_group(required=True)
    end.add_argument("--end-rc", nargs=2, type=int, metavar=("ROW", "COL"))
    end.add_argument("--end-en", nargs=2, type=float, metavar=("EASTING", "NORTHING"))
    parser.add_argument("--start-poi", default=None, metavar="ID")
    parser.add_argument("--end-poi", default=None, metavar="ID")
    parser.add_argument("--slope", type=Path, default=REPO_ROOT / "data" / "processed" / "slope.npy")
    parser.add_argument("--grid", type=Path, default=REPO_ROOT / "data" / "processed" / "grid.json")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "routing" / "config.json")
    parser.add_argument(
        "--exclude",
        default=None,
        metavar="LAYER",
        help="remove one layer (an id from layers.json) from the cost; writes route_<name>_no_<layer>.geojson",
    )
    parser.add_argument(
        "--layers",
        type=Path,
        default=REPO_ROOT / "data" / "processed" / "layers" / "layers.json",
        help="layers.json used to validate --exclude",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry. Returns the exit code; invalid arguments exit via argparse (code 2)."""
    args = _build_parser().parse_args(argv)
    try:
        validate_name(args.name)
        out_name = args.name
        data_used: list[str] | None = None
        slope_removed = False
        if args.exclude is not None:
            layer_ids = load_layer_ids(args.layers)
            if args.exclude not in layer_ids:
                raise RoutingError(
                    f"unknown layer {args.exclude!r} for --exclude; valid layers: {', '.join(layer_ids)}", 2
                )
            out_name = f"{args.name}_no_{args.exclude}"
            validate_name(out_name)
        params, raw_config = load_config(args.config)
        if args.exclude is not None:
            cost_inputs = load_cost_inputs(raw_config, args.config, layer_ids)
            data_used = [layer for layer in cost_inputs if layer != args.exclude]
            slope_removed = "slope" in cost_inputs and "slope" not in data_used
            if args.exclude not in cost_inputs:
                print(f"note: layer '{args.exclude}' is not a cost input: no effect on routing", file=sys.stderr)
        grid = load_grid(args.grid)
        slope = load_slope(args.slope, grid)
        if grid.width is None or grid.height is None:
            grid = replace(grid, width=slope.shape[1], height=slope.shape[0])
        start_spec = (
            EndpointSpec("pixel", *args.start_rc)
            if args.start_rc is not None
            else EndpointSpec("coord", *args.start_en)
        )
        end_spec = (
            EndpointSpec("pixel", *args.end_rc)
            if args.end_rc is not None
            else EndpointSpec("coord", *args.end_en)
        )
        start = resolve_endpoint("start", start_spec, grid)
        end = resolve_endpoint("end", end_spec, grid)
        cost = build_cost_raster(slope, params, grid.nodata_value, slope_removed)
        path, _ = find_path(cost, start, end, params.connectivity)
        feature = build_feature(
            out_name, path, slope, grid, params, raw_config,
            args.start_poi, args.end_poi, get_commit_hash(),
            data_used, args.exclude, grid.nodata_value,
        )
        target = write_route(feature, out_name)
    except RoutingError as exc:
        print(f"error: {exc.message}", file=sys.stderr)
        return exc.exit_code
    print(f"routing/out/route_{out_name}.geojson {os.path.getsize(target)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
