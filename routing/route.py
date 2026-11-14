"""Least-cost route tool (role B). Core types and config loading."""

from __future__ import annotations

import datetime
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

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
