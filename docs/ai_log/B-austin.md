# AI log: Austin (B)

Add one line every time an AI tool helps you. Write in English.
Format: date time | tool and model | what you asked | what it did | how you checked it

2026-11-14 | Kiro (Auto) | Add --exclude <layer> to route.py per spec section 5 | Wrote spec b-routing-exclude, added the switch, config key cost_inputs and README notes | Ran the CLI on the fake and real grid (normal, slope, hillshade, ctx, invalid layer), checked properties against INTERFACES.md, ran pytest (10 passed)