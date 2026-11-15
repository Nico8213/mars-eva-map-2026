# AI log: Austin (B)

Add one line every time an AI tool helps you. Write in English.
Format: date time | tool and model | what you asked | what it did | how you checked it

2026-11-14 | Kiro (Auto) | Add --exclude <layer> to route.py per spec section 5 | Wrote spec b-routing-exclude, added the switch, config key cost_inputs and README notes | Ran the CLI on the fake and real grid (normal, slope, hillshade, ctx, invalid layer), checked properties against INTERFACES.md, ran pytest (10 passed)
2026-11-15 | Kiro (Auto) | Add the --exclude switch for F10 | Added the switch to the routing CLI | Ran route.py with --exclude, checked the output file names, and pytest passed (10 passed)
2026-11-15 | Kiro (Auto) | Write validation/check_transform.py with Checks A, B, C for the b-validation-checks spec | Wrote the script with transform checks A, B, C and its tests | Ran the script on the real snapshot, ran the tests, and checked the printed results myself
2026-11-15 | Kiro (Auto) | Lock validation params v1.0 | Fixed the validation parameters at version 1.0 | Ran check_params_complete.py, which reported no missing items, then committed d1965fd before any validation run
2026-11-15 | Kiro (Auto) | Generate 4 real routes from the landing point to poi-001..004 | Produced the four routes | Ran route.py 4 times with .\.venv\Scripts\python.exe, checked all four routes were reachable and max slope was at most 20 degrees
2026-11-15 | Kiro (Auto) | Write validation/run_validation.py and its tests for the b-validation-run spec | Wrote the script and its tests, which abort if report.json already exists | Ran the tests, then ran the script once on the real data and read the numbers in validation/out/report.json myself
2026-11-14 | not sure | Build the least-cost router in routing/route.py | Wrote the router from skeleton to command line: input loading, endpoint resolution, path search with skimage.graph.route_through_array, GeoJSON output | not remembered
2026-11-14 | not sure | Cost function for the router | Cost = cost_base + cost_coefficient * (slope / slope_limit_deg) ^ cost_exponent, with slope above slope_limit_deg treated as impassable | not remembered
2026-11-15 | Claude chat, model not sure | Step-by-step help with git commands, Kiro approvals, Kiro prompts and group messages for the validation work | Gave the steps and wording | I ran the commands and checked the printed output myself