"""
step5_cards.py — Build data cards (one card for now: hirise_dtm_006).

Reads:
  data/processed/grid.json                  — product, version, pixel size, DOI, known_issue
  data/processed/layers/layers.json         — data_card_id cross-check
  data/processed/sources.md                 — "Known issues" line

Writes:
  data/processed/data_cards.json

Usage:
    .venv/Scripts/python.exe pipeline/step5_cards.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT   = Path(__file__).parent.parent
grid_path   = REPO_ROOT / "data" / "processed" / "grid.json"
layers_path = REPO_ROOT / "data" / "processed" / "layers" / "layers.json"
sources_path = REPO_ROOT / "data" / "processed" / "sources.md"
out_path    = REPO_ROOT / "data" / "processed" / "data_cards.json"

KNOWN_ISSUES_PREFIX = "- Known issues:"
SOURCES_ISSUE_PHRASE = "stereo DTM artifacts and seams"


def fail(msg):
    print(f"Error: {msg}")
    sys.exit(1)


def num_text(x):
    """1.0 -> '1', 0.5 -> '0.5' (no invented precision)."""
    return str(int(x)) if float(x).is_integer() else str(x)


for p in (grid_path, layers_path, sources_path):
    if not p.exists():
        fail(f"input not found: {p}")

with open(grid_path, encoding="utf-8") as f:
    grid = json.load(f)
with open(layers_path, encoding="utf-8") as f:
    layers = json.load(f)
sources_text = sources_path.read_text(encoding="utf-8")

for key in ("source_product", "version", "pixel_size_m", "doi", "known_issue"):
    if not grid.get(key):
        fail(f"grid.json is missing '{key}'")

# Second known issue: first item of the sources.md "Known issues" line
issue_line = next(
    (ln.strip() for ln in sources_text.splitlines() if ln.strip().startswith(KNOWN_ISSUES_PREFIX)),
    None,
)
if issue_line is None:
    fail(f"sources.md has no line starting with '{KNOWN_ISSUES_PREFIX}'")
sources_issue = issue_line[len(KNOWN_ISSUES_PREFIX):].split(";")[0].strip()
if sources_issue != SOURCES_ISSUE_PHRASE:
    fail(f"sources.md known issue is '{sources_issue}', expected '{SOURCES_ISSUE_PHRASE}'")

card = {
    "id": "hirise_dtm_006",
    "layer_name": "Slope and Hillshade (HiRISE DTM)",
    "mission": "MRO",
    "instrument": "HiRISE",
    "product": f"{grid['source_product']}, version {grid['version']}",
    "acquisition_date": "2006-01-01 to 2019-10-24 (USGS 'Time Period of Content')",
    "resolution": f"{num_text(grid['pixel_size_m'])} m/px",
    "license": "Access constraints: None. Use constraints: Please cite authors. No license text found (USGS product page, checked 2026-11-14)",
    "known_issues": [grid["known_issue"], sources_issue],
    "confidence_layer": None,
    "decision_affected": None,
    "verification_status": "candidate",
    "source_url": f"https://doi.org/{grid['doi']}",
}
ctx_card = {
    "id": "ctx_orthomosaic_008",
    "layer_name": None,
    "mission": "MRO",
    "instrument": "CTX",
    "product": "JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0, version 008 (from file name)",
    "acquisition_date": "2006-01-01 to 2019-08-20 (USGS 'Time Period of Content')",
    "resolution": "6 m/px",
    "license": "Access constraints: None. Use constraints: Please cite authors. No license text found (USGS product page, checked 2026-11-14)",
    "known_issues": [
        "Per USGS: individual CTX images have an average horizontal displacement of 9.6 m; a small gap in the northwest corner of the full mosaic was filled with an image orthorectified to HRSC DTM"
    ],
    "confidence_layer": None,
    "decision_affected": None,
    "verification_status": "candidate",
    "source_url": "https://doi.org/10.5066/P9GV1ND3",
}
cards = [card, ctx_card]

with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cards, f, indent=2, ensure_ascii=False)
    f.write("\n")

# Every layer's data_card_id must resolve to a card
card_ids = {c["id"] for c in cards}
missing = sorted({l.get("data_card_id") for l in layers} - card_ids)
if missing:
    fail(f"layers.json data_card_id with no matching card: {missing}")

print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")
