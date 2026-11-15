"""Smoke test for the synthetic repository fixture."""

import json

from conftest import REAL_REPORT, sha256_upper


def test_synthetic_repo_hashes_match(synthetic_repo):
    p = json.loads(synthetic_repo.params_path.read_text(encoding="utf-8"))
    assert p["terrain_integrity"]["sha256_slope_npy"]["value"] == sha256_upper(synthetic_repo.slope_path)
    assert p["terrain_integrity"]["sha256_grid_json"]["value"] == sha256_upper(synthetic_repo.grid_path)
    assert p["reference_path"]["places"]["sha256"]["value"] == sha256_upper(synthetic_repo.places_path)
    assert synthetic_repo.slope.shape == (synthetic_repo.grid["height"], synthetic_repo.grid["width"])
    assert not REAL_REPORT.exists()
