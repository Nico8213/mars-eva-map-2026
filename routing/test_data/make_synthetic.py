"""Generate a synthetic slope map and grid description for testing the router.

Writes routing/test_data/slope.npy and routing/test_data/grid.json.
All data is SYNTHETIC and carries no real terrain information.

Usage:
    python routing/test_data/make_synthetic.py --seed INT
        [--width N] [--height N] [--pixel-size M] [--config PATH]

Grids need room for a flat block (>= 10 cells), a steep block (>= 10 cells)
and one NaN cell without overlap, so at least 21 cells are required. Sizes
where no such layout fits (for example 1x1, or 1x21 is fine but 1x20 is not)
are rejected with an error.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from skimage.filters import gaussian

OUT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = OUT_DIR.parent / "config.json"
MAX_FILE_BYTES = 52_428_800
MIN_BLOCK_CELLS = 10
MIN_SIZE, MAX_SIZE = 1, 1024
NPY_HEADER_BYTES = 128  # numpy format 1.0 header for 2D float32 arrays
FLAT_VALUE = 0.5


def _block_dims(width: int, height: int) -> list[tuple[int, int]]:
    """Candidate (block_h, block_w) rectangles of at least 10 cells."""
    dims = []
    for bw in range(min(width, MIN_BLOCK_CELLS), 0, -1):
        bh = math.ceil(MIN_BLOCK_CELLS / bw)
        if bh <= height:
            dims.append((bh, bw))
    return dims


def _plan_layout(width: int, height: int):
    """Return (flat_slices, steep_slices, nan_cell) or None if nothing fits."""
    for bh, bw in _block_dims(width, height):
        flat = (slice(0, bh), slice(0, bw))
        steep = (slice(height - bh, height), slice(width - bw, width))
        used = np.zeros((height, width), dtype=bool)
        used[flat] = True
        if used[steep].any():
            continue
        used[steep] = True
        free = np.argwhere(~used)
        if len(free) == 0:
            continue
        # Free cell closest to the grid centre (ties: first in row-major order).
        cr, cc = (height - 1) / 2, (width - 1) / 2
        d = (free[:, 0] - cr) ** 2 + (free[:, 1] - cc) ** 2
        r, c = free[int(np.argmin(d))]
        return flat, steep, (int(r), int(c))
    return None


def validate_size(width: int, height: int) -> None:
    for name, v in (("width", width), ("height", height)):
        if isinstance(v, bool) or not isinstance(v, int) or not MIN_SIZE <= v <= MAX_SIZE:
            raise ValueError(f"{name} must be an integer from {MIN_SIZE} to {MAX_SIZE}, got {v!r}")
    if NPY_HEADER_BYTES + width * height * 4 >= MAX_FILE_BYTES:
        raise ValueError(
            f"slope.npy for {width}x{height} would reach the {MAX_FILE_BYTES} byte limit"
        )
    if _plan_layout(width, height) is None:
        raise ValueError(
            f"a {width}x{height} grid cannot hold a flat block (>= {MIN_BLOCK_CELLS} cells), "
            f"a steep block (>= {MIN_BLOCK_CELLS} cells) and a NaN cell without overlap"
        )


def generate(seed, width, height, pixel_size_m, steep_deg):
    """Return (slope float32 array (height, width), grid dict). Pure, no disk I/O."""
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError(f"seed must be a non-negative integer, got {seed!r}")
    validate_size(width, height)
    if not (isinstance(pixel_size_m, (int, float)) and math.isfinite(pixel_size_m) and pixel_size_m > 0):
        raise ValueError(f"pixel size must be a finite number greater than 0, got {pixel_size_m!r}")
    if not (isinstance(steep_deg, (int, float)) and math.isfinite(steep_deg) and steep_deg > 0):
        raise ValueError(f"steep_deg must be a finite number greater than 0, got {steep_deg!r}")

    rng = np.random.default_rng(int(seed))
    noise = gaussian(rng.standard_normal((height, width)), sigma=2.0, mode="reflect")
    lo, hi = float(noise.min()), float(noise.max())
    scaled = np.full((height, width), 2.0) if hi == lo else 2.0 + 13.0 * (noise - lo) / (hi - lo)

    flat, steep, nan_cell = _plan_layout(width, height)
    scaled[flat] = FLAT_VALUE
    scaled[steep] = min(float(steep_deg), 90.0)
    scaled[nan_cell] = np.nan

    slope = np.clip(scaled, 0.0, 90.0).astype(np.float32)  # clip keeps NaN as NaN

    grid = {
        "pixel_size_m": float(pixel_size_m),
        "width": int(width),
        "height": int(height),
        "top_left": {"easting_m": 0.0, "northing_m": float(height * pixel_size_m)},
        "crs": "SYNTHETIC (no real projection)",
        "synthetic": True,
        "nodata_value": None,
    }
    return slope, grid


def read_slope_limit(config_path: Path) -> float:
    try:
        with open(config_path, encoding="utf-8") as f:
            limit = json.load(f)["slope_limit_deg"]["value"]
    except OSError as e:
        raise ValueError(f"cannot read config file {config_path}: {e}") from e
    except (ValueError, KeyError, TypeError) as e:
        raise ValueError(f"config file {config_path} is invalid or lacks slope_limit_deg.value: {e!r}") from e
    if isinstance(limit, bool) or not isinstance(limit, (int, float)) or not math.isfinite(limit) or limit <= 0:
        raise ValueError(f"slope_limit_deg.value must be a finite number greater than 0, got {limit!r}")
    return float(limit)


def write_outputs(slope, grid, out_dir: Path = OUT_DIR) -> list[tuple[Path, int]]:
    """Write both files via temp names, then os.replace both."""
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = {"slope.npy": out_dir / "slope.npy", "grid.json": out_dir / "grid.json"}
    tmps = {k: out_dir / (k + ".tmp") for k in targets}
    try:
        with open(tmps["slope.npy"], "wb") as f:
            np.save(f, slope, allow_pickle=False)
        with open(tmps["grid.json"], "w", encoding="utf-8", newline="\n") as f:
            json.dump(grid, f, sort_keys=True, indent=2)
            f.write("\n")
        for k, tmp in tmps.items():
            size = tmp.stat().st_size
            if size >= MAX_FILE_BYTES:
                raise ValueError(f"{k} is {size} bytes, over the {MAX_FILE_BYTES} byte limit")
        sizes = {k: tmps[k].stat().st_size for k in tmps}
        for k in tmps:
            os.replace(tmps[k], targets[k])
    except BaseException:
        for tmp in tmps.values():
            try:
                tmp.unlink()
            except OSError:
                pass
        raise
    return [(targets[k], sizes[k]) for k in ("slope.npy", "grid.json")]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Generate synthetic slope.npy and grid.json in routing/test_data/.")
    p.add_argument("--seed", type=int, required=True, help="integer seed (>= 0)")
    p.add_argument("--width", type=int, default=64, help="cells, 1 to 1024 (default 64)")
    p.add_argument("--height", type=int, default=64, help="cells, 1 to 1024 (default 64)")
    p.add_argument("--pixel-size", type=float, default=1.0, help="metres per cell (default 1.0)")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="path to routing config.json")
    args = p.parse_args(argv)  # exits with status 2 on missing or non-integer seed

    try:
        limit = read_slope_limit(args.config)
        steep = min(limit + 10.0, 90.0)
        slope, grid = generate(args.seed, args.width, args.height, args.pixel_size, steep)
        written = write_outputs(slope, grid)
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for path, size in written:
        print(f"{path} {size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
