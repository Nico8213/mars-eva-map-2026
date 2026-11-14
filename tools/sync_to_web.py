#!/usr/bin/env python3
"""Copy pipeline output into web/public/data/ for the web cockpit.

Sources (read only):
    data/processed/layers/        -> web/public/data/layers/
    data/processed/layers.json    -> web/public/data/layers/layers.json
    data/processed/poi.geojson    -> web/public/data/poi.geojson
    data/processed/data_cards.json-> web/public/data/data_cards.json
    routing/out/*.geojson         -> web/public/data/routes/ (plus routes/index.json)
    validation/out/report.json    -> web/public/data/report.json

A missing source prints a notice and the script continues. Nothing is deleted.
Uses only the Python standard library. Run: python tools/sync_to_web.py
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
ROUTING_OUT = ROOT / "routing" / "out"
VALIDATION_OUT = ROOT / "validation" / "out"
DEST = ROOT / "web" / "public" / "data"

MAX_BYTES = 50 * 1024 * 1024  # project rule: no file over 50 MB

written = {}  # destination path -> None (ordered, no duplicates)
failed = []   # messages for files that could not be copied


def rel(path):
    """Path relative to the repository root, with forward slashes."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def copy_file(src, dst):
    """Copy one file. Returns True when it was written."""
    try:
        if src.stat().st_size > MAX_BYTES:
            print(f"Too large (over 50 MB), skipped: {rel(src)}")
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    except OSError as err:
        message = f"Failed to copy {rel(src)}: {err}"
        print(message)
        failed.append(message)
        return False
    written[dst] = None
    return True


def sync_file(src, dst):
    """Copy one file if it exists, otherwise print a notice."""
    if not src.is_file():
        print(f"Not found, skipped: {rel(src)}")
        return False
    return copy_file(src, dst)


def sync_folder(src_dir, dst_dir):
    """Copy every file under src_dir, keeping sub-paths."""
    if not src_dir.is_dir():
        print(f"Not found, skipped: {rel(src_dir)}/")
        return
    # Hidden files such as .gitkeep are placeholders, not data.
    files = sorted(
        p for p in src_dir.rglob("*") if p.is_file() and not p.name.startswith(".")
    )
    if not files:
        print(f"No files in {rel(src_dir)}/, skipped")
        return
    for src in files:
        copy_file(src, dst_dir / src.relative_to(src_dir))


def sync_glob(src_dir, pattern, dst_dir):
    """Copy files that match pattern in src_dir. Returns the copied file names."""
    if not src_dir.is_dir():
        print(f"Not found, skipped: {rel(src_dir)}/")
        return []
    files = sorted(p for p in src_dir.glob(pattern) if p.is_file())
    if not files:
        print(f"No {pattern} files in {rel(src_dir)}/, skipped")
        return []
    copied = []
    for src in files:
        if copy_file(src, dst_dir / src.name):
            copied.append(src.name)
    return copied


def write_route_index(names):
    """Write routes/index.json, the list of route files the cockpit loads."""
    index_path = DEST / "routes" / "index.json"
    try:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(sorted(names), indent=2) + "\n"
        with open(index_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except OSError as err:
        message = f"Failed to write {rel(index_path)}: {err}"
        print(message)
        failed.append(message)
        return
    written[index_path] = None


def main():
    # Folder first, so the separate layers.json replaces any copy from inside it.
    sync_folder(PROCESSED / "layers", DEST / "layers")
    sync_file(PROCESSED / "layers.json", DEST / "layers" / "layers.json")
    sync_file(PROCESSED / "poi.geojson", DEST / "poi.geojson")
    sync_file(PROCESSED / "data_cards.json", DEST / "data_cards.json")

    routes = sync_glob(ROUTING_OUT, "*.geojson", DEST / "routes")
    if routes:
        write_route_index(routes)

    sync_file(VALIDATION_OUT / "report.json", DEST / "report.json")

    for path in written:
        print(f"wrote {rel(path)} ({path.stat().st_size} bytes)")
    if not written:
        print("Nothing was written.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
