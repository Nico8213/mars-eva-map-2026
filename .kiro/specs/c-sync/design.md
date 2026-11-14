# Design: c-sync

## Overview

One script, `tools/sync_to_web.py`. Standard library only (`pathlib`, `shutil`, `json`, `sys`). It runs a fixed list of copy steps. Each step handles its own missing source, so one gap never stops the run.

## Paths

The repository root is `Path(__file__).resolve().parent.parent`.

| Name | Path |
|---|---|
| `PROCESSED` | `<root>/data/processed` |
| `ROUTING_OUT` | `<root>/routing/out` |
| `VALIDATION_OUT` | `<root>/validation/out` |
| `DEST` | `<root>/web/public/data` |

## Steps (in order)

| # | Step | Source | Destination |
|---|---|---|---|
| 1 | folder | `PROCESSED/layers/` | `DEST/layers/` |
| 2 | file | `PROCESSED/layers.json` | `DEST/layers/layers.json` |
| 3 | file | `PROCESSED/poi.geojson` | `DEST/poi.geojson` |
| 4 | file | `PROCESSED/data_cards.json` | `DEST/data_cards.json` |
| 5 | glob | `ROUTING_OUT/*.geojson` | `DEST/routes/` |
| 6 | index | names copied in step 5 | `DEST/routes/index.json` |
| 7 | file | `VALIDATION_OUT/report.json` | `DEST/report.json` |

Step 2 runs after step 1, so a separate `layers.json` replaces any `layers/layers.json` that came from the folder.

## Functions

```python
copy_file(src, dst) -> bool          # one file: size check, mkdir, copyfile, record
sync_folder(src_dir, dst_dir) -> None   # every file under src_dir, keeps sub-paths
sync_file(src, dst) -> bool          # missing -> notice, else copy_file
sync_glob(src_dir, pattern, dst_dir) -> list[str]   # returns copied file names
write_route_index(names) -> None     # only called when names is not empty
main() -> int                        # runs steps, prints summary, returns exit code
```

State kept in module-level structures: `written` (ordered dict of destination paths) and `failed` (list of messages).

## Behaviour

- **Missing source:** print `Not found, skipped: <relative path>` and continue. This is not an error.
- **Empty folder or no glob match:** print `No files in <relative path>, skipped`.
- **Hidden files:** `sync_folder` ignores files whose name starts with a dot. `data/processed/layers/` holds a `.gitkeep` in the repository, and it must not reach the website.
- **Large file:** if `st_size > 50 * 1024 * 1024`, print `Too large (over 50 MB), skipped: <path>`.
- **OSError while copying:** print `Failed to copy <path>: <reason>`, add to `failed`, continue.
- **Route index:** `json.dumps(sorted(names), indent=2)` plus a final newline, written as UTF-8 with LF line endings. Only written when step 5 copied at least one file.
- **Overwrite:** `shutil.copyfile` replaces the destination. Nothing is deleted.
- **Summary:** after all steps, print `wrote <relative path> (<size> bytes)` for each file in `written`. Exit code is 1 if `failed` is not empty, otherwise 0.
- Output uses forward slashes (`Path.as_posix()`) and ASCII text only, so it prints the same on Windows and other systems.

## Data flow

```
data/processed/layers/ ----------\
data/processed/layers.json ------\\
data/processed/poi.geojson ------- > web/public/data/  -> cockpit (c-web-cockpit)
data/processed/data_cards.json --//
routing/out/*.geojson ----------/   (routes/ + generated routes/index.json)
validation/out/report.json -----/
```

## Testing approach

No test framework is added. Manual checks:

1. Run in the repository as it is now (no `data/processed/`): every source prints "Not found", exit code 0, no file written, `routes/index.json` unchanged.
2. Copy the script into a temporary folder tree with fake sources and run it there: all files land in the right places, `routes/index.json` lists the copied routes, one summary line per file.
3. Remove one source in the temporary tree and run again: one notice line for it, the rest are copied.
4. Put an existing file in a destination: it is replaced, and an unrelated file next to it is untouched.

## Requirements traceability

| Requirement | Covered by |
|---|---|
| R1 | Steps table, step order, `copy_file` mkdir and overwrite |
| R2 | Step 6, `write_route_index` |
| R3 | Missing source and empty folder behaviour, exit code |
| R4 | OSError and large-file behaviour |
| R5 | Paths section, summary line |
