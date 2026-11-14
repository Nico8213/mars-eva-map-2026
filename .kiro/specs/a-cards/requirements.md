# Requirements: a-cards

## Goal
`pipeline/step5_cards.py` writes `data/processed/data_cards.json` (JSON array, 2-space indent, UTF-8). This round produces one card.

## Requirements
1. The card has id `hirise_dtm_006`, equal to the `data_card_id` of both layers in `layers.json`.
2. Field names match the 13 fields of `data_cards.json` in `docs/INTERFACES.md`: `id`, `layer_name`, `mission`, `instrument`, `product`, `acquisition_date`, `resolution`, `license`, `known_issues`, `confidence_layer`, `decision_affected`, `verification_status`, `source_url`.
3. Values:
   - `layer_name`: "Slope and Hillshade (HiRISE DTM)"; `mission`: "MRO"; `instrument`: "HiRISE"
   - `product`: `<source_product>, version <version>` from `grid.json`
   - `resolution`: `<pixel_size_m> m/px` from `grid.json`
   - `source_url`: `https://doi.org/<doi>` from `grid.json`
   - `known_issues`: [`grid.json` `known_issue`, the "stereo DTM artifacts and seams" item from `sources.md` "Known issues"], text unchanged
   - `acquisition_date`, `license`, `confidence_layer`, `decision_affected`: null
   - `verification_status`: "candidate"
4. Values come only from the listed files. Missing values are null.
5. After writing, every `data_card_id` in `layers.json` must match a card `id`. Otherwise the script reports an error and exits non-zero.
6. The script prints the output path and byte count.
7. `grid.json`, `layers.json`, and existing scripts are not modified.
