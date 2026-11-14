# Requirements: c-sync

## Introduction

`tools/sync_to_web.py` copies the data files produced by A and B into `web/public/data/`, where the web cockpit (spec `c-web-cockpit`) reads them. It uses only the Python standard library and never stops because a source file is missing.

Owner: C (`tools/`). The script only reads from `data/`, `routing/` and `validation/` (owned by A and B) and only writes into `web/public/data/`. File formats follow `docs/INTERFACES.md` and are not changed or checked by this script.

## Glossary

- Source: a file or folder written by A or B.
- Destination: a path inside `web/public/data/` (the Data root of the cockpit).
- Sync: copy a source to its destination, replacing an existing file of the same name.

## Requirements

### R1: Files to copy

**User story:** As a web developer, I want one command that brings the latest pipeline output into the website, so that I do not copy files by hand.

Acceptance criteria:
1. THE script SHALL copy these sources to these destinations:

| Source | Destination (in `web/public/data/`) |
|---|---|
| `data/processed/layers/` (all files, recursive) | `layers/` |
| `data/processed/layers.json` | `layers/layers.json` |
| `data/processed/poi.geojson` | `poi.geojson` |
| `data/processed/data_cards.json` | `data_cards.json` |
| `routing/out/*.geojson` | `routes/` |
| `validation/out/report.json` | `report.json` |

2. THE script SHALL copy `data/processed/layers/` first and `data/processed/layers.json` after it, so the separate `layers.json` wins if both exist.
3. THE script SHALL create destination folders when they do not exist.
3a. THE script SHALL skip hidden files (names that start with a dot, such as `.gitkeep`) when it copies a folder.
4. THE script SHALL replace an existing destination file with the same name and SHALL NOT delete any other file in `web/public/data/`.
5. THE script SHALL NOT write outside `web/public/data/` and SHALL NOT change any source file.

### R2: Route index

**User story:** As a user of the cockpit, I want new routes to appear on the map without editing a list by hand.

Acceptance criteria:
1. WHEN at least one route file was copied, THE script SHALL write `routes/index.json` as a JSON array of the copied file names, sorted, with 2-space indentation and UTF-8 encoding.
2. WHEN no route file was copied, THE script SHALL leave `routes/index.json` unchanged.

### R3: Missing files

**User story:** As a team member, I want the script to keep going when a source is not ready yet, so that a partial sync still works.

Acceptance criteria:
1. IF a source file or folder does not exist, THEN THE script SHALL print one line that names the missing path and SHALL continue with the next source.
2. IF a folder exists but has no files, or `routing/out/` has no `*.geojson` file, THEN THE script SHALL print one line saying so and continue.
3. WHEN only missing sources occur, THE script SHALL exit with code 0 and SHALL NOT print a traceback.

### R4: Other copy problems

Acceptance criteria:
1. IF a file cannot be copied because of an operating system error (for example a permission error), THEN THE script SHALL print one line with the path and the reason, continue with the other files and exit with code 1 at the end.
2. IF a source file is larger than 50 MB, THEN THE script SHALL skip it and print one line, because the project rule is that no file in the repository exceeds 50 MB.

### R5: Output and environment

Acceptance criteria:
1. THE script SHALL use only the Python standard library and run with Python 3.12 from the command line with no arguments.
2. THE script SHALL find the repository root from its own location, so it works from any current directory.
3. AT the end, THE script SHALL print one line per file it wrote, with the path relative to the repository root and the size in bytes (project rule in `tech.md`).
4. All output text, comments and identifiers SHALL be in English.

## Out of scope

- Checking file content against `INTERFACES.md`.
- Deleting stale files in `web/public/data/`, including the dummy files from `c-web-cockpit`.
- Copying `grid.json`, `slope.npy` or other files not listed in R1.
- Running the sync automatically (hooks, CI).

## Assumptions to confirm

- `layers.json` is copied to `layers/layers.json` because the cockpit reads it there. `INTERFACES.md` does not say where A places it relative to the PNGs.
- Routes go into `routes/` with a generated `routes/index.json`, as assumed in `c-web-cockpit`.
- Dummy files whose names are not replaced by real data (for example `route_ea-01.geojson`) stay on disk, but a new `index.json` no longer lists them.
