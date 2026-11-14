# Design: a-cards

Inputs: `data/processed/grid.json`, `data/processed/layers/layers.json`, `data/processed/sources.md`.
Output: `data/processed/data_cards.json`.

Flow:
1. Load `grid.json` and `layers.json`; read `sources.md` and find the line starting `- Known issues:`.
2. Take the text before the first `;` as the second known issue (the "stereo DTM artifacts and seams" phrase). If the line or phrase is missing, exit with an error.
3. Build the card with the 13 fields in INTERFACES.md order. Constant fields (id, layer_name, mission, instrument, verification_status) are literals; the rest come from the files or are null.
4. Write JSON with `indent=2`, `ensure_ascii=False`, UTF-8, trailing newline.
5. Check that each `data_card_id` in `layers.json` is a card `id`; otherwise print an error and `sys.exit(1)`.
6. Print the path and byte count.
