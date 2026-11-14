# AI log: Xin En (A)

Add one line every time an AI tool helps you. Write in English.
Format: date time | tool and model | what you asked | what it did | how you checked it

2026-11-14 10:30 | Kiro, Auto | Generate 100x100 synthetic slope.npy and grid.json | Wrote make_sample.py and data/processed/sample/ | Checked array shape and dtype in CMD
2026-11-14 12:17 | Kiro, Auto | Crop the Jezero HiRISE DTM to the area set in config.json | Wrote pipeline/step1_crop_dtm.py and data/raw/cropped_dtm.tif | Checked the output file exists and is about 51 MB in CMD
2026-11-14 13:56 | Kiro, Auto | Compute slope from the cropped DTM and write grid.json | Wrote pipeline/step2_slope.py, data/processed/slope.npy and grid.json | Checked grid.json has width and height 4000 and slope.npy size matches 4000x4000 float32
2026-11-14 14:04 | Kiro, Auto | Make slope and hillshade PNG layers and layers.json | Wrote pipeline/step3_layers.py and files in data/processed/layers/ | Opened both PNGs and they match the terrain; checked layers.json extent values are real degrees
2026-11-14 14:30 | Kiro, Auto | Check that .gitignore ignores data/raw/ | Found data/raw/ already present and made no change | Ran type .gitignore in CMD and saw data/raw/
