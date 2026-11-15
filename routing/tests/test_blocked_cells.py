"""Blocked-cell tests (spec section 4.7, item 5). Synthetic 20x20 grids only."""
import math

import numpy as np
import pytest

from routing.route import RoutingError, find_path, path_cost

N = 20
WALL_ROW = 10
START = (0, 10)
END = (N - 1, 10)


def make_grid(gap_col=None):
    """Flat cost-1 grid with a blocked (np.inf) wall across row WALL_ROW."""
    cost = np.ones((N, N), dtype=np.float64)
    cost[WALL_ROW, :] = np.inf
    if gap_col is not None:
        cost[WALL_ROW, gap_col] = 1.0
    return cost


def assert_valid_run(cost, path, total):
    """Run after every successful route: finite cost, no blocked cell on the path."""
    assert math.isfinite(total)
    assert math.isfinite(path_cost(cost, path))
    assert all(np.isfinite(cost[r, c]) for r, c in path)
    assert not any(np.isposinf(cost[r, c]) for r, c in path)


@pytest.mark.parametrize("connectivity", [4, 8])
def test_full_wall_is_unreachable(connectivity):
    cost = make_grid()
    with pytest.raises(RoutingError) as exc:
        find_path(cost, START, END, connectivity)
    assert exc.value.exit_code == 1


@pytest.mark.parametrize("connectivity", [4, 8])
def test_single_gap_routes_through_gap(connectivity):
    gap_col = 3
    cost = make_grid(gap_col)
    path, total = find_path(cost, START, END, connectivity)
    assert path[0] == START and path[-1] == END
    crossings = [(r, c) for r, c in path if r == WALL_ROW]
    assert crossings == [(WALL_ROW, gap_col)]
    assert_valid_run(cost, path, total)


@pytest.mark.parametrize("gap_col", [0, 7, 19])
@pytest.mark.parametrize("connectivity", [4, 8])
def test_cost_finite_and_no_blocked_cells_on_route(gap_col, connectivity):
    cost = make_grid(gap_col)
    path, total = find_path(cost, START, END, connectivity)
    assert_valid_run(cost, path, total)
