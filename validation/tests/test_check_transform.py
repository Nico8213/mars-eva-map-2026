"""Property tests for validation/check_transform.py (grid loading)."""

import json
import os
import sys
import tempfile

from hypothesis import given, settings, strategies as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math  # noqa: E402

import pytest  # noqa: E402

from check_transform import (  # noqa: E402
    Grid,
    InputError,
    load_grid,
    project_ellipsoid,
    project_eqc,
    project_sphere,
)

FIELDS = ["top_left_x_m", "top_left_y_m", "pixel_size_m", "width", "height"]

coord = st.floats(min_value=-1e7, max_value=1e7, allow_nan=False, allow_infinity=False)
pixel = st.floats(min_value=1e-3, max_value=1e4, allow_nan=False, allow_infinity=False)
dim = st.integers(min_value=1, max_value=100000)

json_scalar = st.one_of(st.none(), st.booleans(), st.integers(-1000, 1000), st.text(max_size=10))
extra_keys = st.dictionaries(
    st.text(min_size=1, max_size=10).filter(lambda k: k not in FIELDS),
    json_scalar,
    max_size=5,
)
top_left_coordinate = st.fixed_dictionaries(
    {
        "lon": st.floats(-1e3, 1e3, allow_nan=False, allow_infinity=False),
        "lat": st.floats(-1e3, 1e3, allow_nan=False, allow_infinity=False),
    }
)


@st.composite
def valid_grids(draw):
    data = {
        "top_left_x_m": draw(coord),
        "top_left_y_m": draw(coord),
        "pixel_size_m": draw(pixel),
        "width": draw(dim),
        "height": draw(dim),
    }
    data.update(draw(extra_keys))
    if draw(st.booleans()):
        data["top_left_coordinate"] = draw(top_left_coordinate)
    if draw(st.booleans()):
        data["coordinate_notes"] = draw(st.text(max_size=30))
    return data


def _load(data):
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle)
        return load_grid(path)
    finally:
        os.remove(path)


def _expected(data):
    return Grid(
        top_left_x_m=float(data["top_left_x_m"]),
        top_left_y_m=float(data["top_left_y_m"]),
        pixel_size_m=float(data["pixel_size_m"]),
        width=data["width"],
        height=data["height"],
    )


# Feature: b-validation-checks, Property 3: Grid loading depends only on the five fields
# **Validates: Requirements 1.3, 1.4, 1.6, 1.7**
@settings(max_examples=100, deadline=None)
@given(data=valid_grids())
def test_extra_keys_do_not_change_grid(data):
    assert _load(data) == _expected(data)
    core = {k: data[k] for k in FIELDS}
    assert _load(core) == _load(data)


# Feature: b-validation-checks, Property 3: Grid loading depends only on the five fields
# **Validates: Requirements 1.3, 1.4, 1.6, 1.7**
@settings(max_examples=100, deadline=None)
@given(data=valid_grids(), removed=st.sets(st.sampled_from(FIELDS), min_size=1))
def test_removed_fields_are_all_named(data, removed):
    for name in removed:
        del data[name]
    try:
        _load(data)
    except InputError as err:
        assert err.problem == "missing_field"
        for name in removed:
            assert name in err.field
        assert set(err.field.split(", ")) == removed
    else:
        raise AssertionError("expected InputError")


bad_pixel = st.one_of(
    st.booleans(),
    st.floats(max_value=0, allow_nan=False, allow_infinity=False),
    st.integers(max_value=0),
    st.text(max_size=5),
    st.none(),
    st.lists(st.integers(), max_size=2),
)
bad_dim = st.one_of(
    st.booleans(),
    st.integers(max_value=0),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(max_size=5),
    st.none(),
)


# Feature: b-validation-checks, Property 3: Grid loading depends only on the five fields
# **Validates: Requirements 1.3, 1.4, 1.6, 1.7**
@settings(max_examples=100, deadline=None)
@given(data=valid_grids(), field=st.sampled_from(["pixel_size_m", "width", "height"]), pick=st.data())
def test_invalid_values_rejected(data, field, pick):
    data[field] = pick.draw(bad_pixel if field == "pixel_size_m" else bad_dim)
    try:
        _load(data)
    except InputError as err:
        assert err.problem == "invalid_value"
        assert err.field == field
    else:
        raise AssertionError("expected InputError")


lon_st = st.floats(min_value=-180, max_value=360, allow_nan=False, allow_infinity=False)
lat_st = st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False)
radius_st = st.floats(min_value=1.0, max_value=1e8, allow_nan=False, allow_infinity=False)


# Feature: b-validation-checks, Property 1: Projection formula matches an independent calculation
# **Validates: Requirements 1.1**
@settings(max_examples=100, deadline=None)
@given(lon=lon_st, lat=lat_st, radius=radius_st)
def test_projection_matches_independent_calculation(lon, lat, radius):
    x, y = project_eqc(lon, lat, radius)
    assert x == pytest.approx(radius * lon * math.pi / 180, rel=1e-9, abs=1e-6)
    assert y == pytest.approx(radius * lat * math.pi / 180, rel=1e-9, abs=1e-6)

    for func in (project_sphere, project_ellipsoid):
        sx, sy = func(lon, lat)
        assert sx == pytest.approx(3396190 * lon * math.pi / 180, rel=1e-9, abs=1e-6)
        assert sy == pytest.approx(3396190 * lat * math.pi / 180, rel=1e-9, abs=1e-6)
