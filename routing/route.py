"""Least-cost route tool (role B). Core types and config loading."""

from __future__ import annotations

import datetime
import json
import math
import re
from dataclasses import dataclass
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
    width: int
    height: int
    easting_m: float  # top_left.easting_m
    northing_m: float  # top_left.northing_m
    crs: str


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


_GRID_FIELDS = ("pixel_size_m", "width", "height", "top_left", "crs")


def _is_number(v: object) -> bool:
    return not isinstance(v, bool) and isinstance(v, (int, float))


def load_grid(path: Path) -> Grid:
    """Read and validate grid.json. Raises RoutingError (exit code 2)."""
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

    missing = [k for k in _GRID_FIELDS if k not in raw]
    if missing:
        raise fail("missing required field(s): " + ", ".join(missing))

    px = raw["pixel_size_m"]
    if not _is_number(px) or not math.isfinite(px) or px <= 0:
        raise fail(f"field 'pixel_size_m' must be a number greater than 0 (rejected value: {px!r})")
    for key in ("width", "height"):
        v = raw[key]
        if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
            raise fail(f"field '{key}' must be an integer greater than 0 (rejected value: {v!r})")

    tl = raw["top_left"]
    if not isinstance(tl, dict):
        raise fail(f"field 'top_left' must be an object (rejected value: {tl!r})")
    for key in ("easting_m", "northing_m"):
        if key not in tl:
            raise fail(f"missing required field(s): top_left.{key}")
        v = tl[key]
        if not _is_number(v) or not math.isfinite(v):
            raise fail(f"field 'top_left.{key}' must be a finite number (rejected value: {v!r})")

    crs = raw["crs"]
    if not isinstance(crs, str) or not crs.strip():
        raise fail(f"field 'crs' must be a non-empty string (rejected value: {crs!r})")

    return Grid(
        pixel_size_m=float(px),
        width=raw["width"],
        height=raw["height"],
        easting_m=float(tl["easting_m"]),
        northing_m=float(tl["northing_m"]),
        crs=crs,
    )


def load_slope(path: Path, grid: Grid) -> np.ndarray:
    """Read slope.npy and check it is 2D with shape (height, width)."""
    path = Path(path)

    def fail(detail: str) -> RoutingError:
        return RoutingError(f"slope file {path}: {detail}", 2)

    try:
        arr = np.load(path, allow_pickle=False)
    except FileNotFoundError:
        raise fail("file not found") from None
    except Exception as exc:  # invalid NumPy file, pickled object, unreadable
        raise fail(f"not a valid NumPy array file ({exc})") from None
    if not isinstance(arr, np.ndarray):
        raise fail("not a single NumPy array")
    if arr.ndim != 2:
        raise fail(f"slope array must have 2 dimensions, found {arr.ndim}")
    expected = (grid.height, grid.width)
    if arr.shape != expected:
        raise fail(f"slope array shape {arr.shape} does not match grid (height, width) {expected}")
    return arr


def build_cost_raster(slope: np.ndarray, p: CostParams) -> np.ndarray:
    """Per-pixel traversal cost (float64). NaN and slopes above the limit are np.inf."""
    s = np.abs(np.asarray(slope, dtype=np.float64))
    cost = np.full(s.shape, np.inf, dtype=np.float64)
    ok = s <= p.slope_limit_deg  # False for NaN
    cost[ok] = p.cost_base + p.cost_coefficient * (s[ok] / p.slope_limit_deg) ** p.cost_exponent
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
