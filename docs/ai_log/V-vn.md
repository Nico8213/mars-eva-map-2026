# AI log: VN (V)

Add one line every time an AI tool helps you. Write in English.
Format: date time | tool and model | what you asked | what it did | how you checked it

# AI log - V (VN)

Role: data facts research and website testing (weak computer, browser only, no Kiro).
This log lists every AI tool used by VN, what it was used for, and what a human checked.
Rule followed: no number or claim goes into a research card without a source link; where a source could not be checked, the card says so.

## Log

| Date | Who | Tool and model | What it was used for | Human check |
| --- | --- | --- | --- | --- |
| 2026-11-14 | VN | Claude (claude.ai chat, Claude Sonnet 5.5, web search on) | Walked through the task guide and listed VN's tasks and deadlines for day 1 | VN compared the list with the task guide, section 10 |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched the web for CRISM product information and drafted `docs/research/vn-crism.md` (instrument and timeline, archive and versions, product types, resolution, Jezero coverage, license and citation, known issues) | [VN: opened each link and checked the page] |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched for radiation and dust sources and drafted `docs/research/vn-env-sources.md`; later revised it after reading the original Hassler et al. (Science 2014) paper copy and the Nature Geoscience MEDA paper page | [VN: same as above] |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched for Jezero geology background and drafted `docs/research/vn-geology.md` | [VN: same as above] |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Read the PDS Rover PLACES page, release notes and Software Interface Specification and drafted `docs/research/vn-perseverance-traverse.md` | [VN: same as above] |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched for Jezero rock and mineral data sets and drafted `docs/research/vn-rocks.md` | [VN: same as above] |
| 2026-11-14 | VN | Claude (claude.ai) | Explained how to create files and commit on GitHub in the browser; checked screenshots of the commit dialog (file name, commit message format, branch choice) | VN committed the files herself/himself |

## What the AI did NOT do
- It did not download any data file (the AI session could not download PDS or Zenodo files), so file sizes and row counts in the cards are copied from web pages or marked as unknown.
- It did not write code for the project and did not touch the repository; VN created every file by hand in the GitHub web interface.
- It did not produce any validation number; all numbers in the cards are copied from the cited sources.

## Mistakes found and corrected
- An early draft of the Gale crater radiation card gave a dose equivalent of 0.67 mSv/day (from a press release). After reading the paper itself the card now uses 0.64 +/- 0.12 mSv/day.
- An early draft gave the Nature Geoscience MEDA paper year as 2022; the correct publication year is 2023.
- Early drafts mixed Opportunity and Gale values into the "Jezero" environment cards; after VN asked for Jezero-only values, every card now says where a value was measured and Jezero data were added.
- An unverified claim from a second check list (Mendeley data set license "blank") was not used; the Mendeley page itself shows CC BY 4.0.

## Entries for 15 Nov (fill in as you go)
| Date | Who | Tool and model | What it was used for | Human check |
| --- | --- | --- | --- | --- |

## Short paragraph for docs/SUBMISSION.md (AI tools used)
VN used Claude (Anthropic, claude.ai with web search) to find and summarize public sources about CRISM data, Mars radiation and dust, Jezero geology, the Perseverance traverse data and Jezero rock data, and to draft the research cards in docs/research/. Every claim in a card carries a source link, and where a source could not be checked the card says so. VN opened and checked the cited pages, created and committed the files by hand, and tested the website in a browser. The AI did not write project code, did not download data, and did not produce any validation result.

