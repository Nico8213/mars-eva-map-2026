# Reproduce

## Requirements

TBD

## Data download

TBD

## Pipeline

TBD

## Routing

See routing/README.md for how routes are produced. Route GeoJSON coordinates are grid metres, not longitude/latitude.

## Validation

Run these commands in Windows PowerShell from the repository root.

Step 1, check the coordinate transform:

```powershell
.\.venv\Scripts\python.exe validation\check_transform.py
```

Output: `validation/out/check_transform.json`

Step 2, validate against the Perseverance traverse:

```powershell
.\.venv\Scripts\python.exe validation\run_validation.py
```

Output: `validation/out/report.json`

Note: this script was run once, after the parameters were locked (commit d1965fd). Do not edit `validation/params.json` and do not re-run it to tune results. Do not commit a re-generated `validation/out/report.json`. The committed report is the single run made after the parameters were locked (d1965fd). The result is a weak match, and the report records it as measured.

## Web preview

TBD
