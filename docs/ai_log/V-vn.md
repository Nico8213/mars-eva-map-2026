# AI log - V (VN)

Role: data facts research and website testing (weak computer, browser only, no Kiro).
This log lists every AI tool used by VN, what it was used for, and what a human checked.
Rule followed: no number or claim goes into a research card without a source link; where a source could not be checked, the card says so.

## Log

| Date | Who | Tool and model | What it was used for | Human check |
| --- | --- | --- | --- | --- |
| 2026-11-14 | VN | Claude (claude.ai chat, Claude Sonnet 5.5, web search on) | Walked through the task guide and listed VN's tasks and deadlines for day 1 | VN compared the list with the task guide, section 10 |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched the web for CRISM product information and drafted `docs/research/vn-crism.md` (instrument and timeline, archive and versions, product types, resolution, Jezero coverage, license and citation, known issues) | VN opened all source links in the card and compared the instrument dates (2006-09-27 to 2022-05-07), the MRDR version 4 date (2022-06-29) and the PDS FAQ public-domain and TSPA wording with the pages; all matched |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched for radiation and dust sources and drafted `docs/research/vn-env-sources.md`; later revised it after reading the original Hassler et al. (Science 2014) paper copy and the Nature Geoscience MEDA paper page | VN opened all source links and compared the Gale dose values (0.210 mGy/day, 0.64 mSv/day), the Jezero SkyCam optical depth (about 0.5 morning, 0.4 afternoon), the pressure values (735, 761, 650 Pa), the January 2022 storm peak (about 2) and the Mendeley license field (CC BY 4.0) with the pages; all matched |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched for Jezero geology background and drafted `docs/research/vn-geology.md` | VN opened all source links and compared the crater size and announcement date (NASA, 2018-11-19), the igneous floor units (Seitah, Maaz) and the delta age (about 3.7 billion years) with the pages; all matched |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Read the PDS Rover PLACES page, release notes and Software Interface Specification and drafted `docs/research/vn-perseverance-traverse.md` | VN opened all source links and compared the PLACES release (Release 16, 2026-08-11, sols 0-1897), the 0.5 m localization accuracy in the SIS and the date difference in the release notes with the pages; all matched |
| 2026-11-14 | VN | Claude (claude.ai, web search on) | Searched for Jezero rock and mineral data sets and drafted `docs/research/vn-rocks.md` | VN opened all source links and compared the USGS map (SIM 3464, 349.3 MB database, scale 1:75,000) and the Zenodo data set (CC BY 4.0, 6.8 GB model data, 60.7 kB regions file) with the pages; all matched |
| 2026-11-14 | VN | Claude (claude.ai) | Explained how to create files and commit on GitHub in the browser; checked screenshots of the commit dialog (file name, commit message format, branch choice) | VN created and committed every research file by hand and checked the GitHub commit history to confirm the files are in docs/research/ |
| 2026-11-15 | VN | Claude (claude.ai, web search on) | Checked the NASA location-map page, PLACES and the PRD text; drafted the updated vn-perseverance-traverse.md and the F10 proposal | VN compared the NASA page text (no link to the two JSON files, no license text) and the PRD section 7.4 snapshot numbers (2026-10-11, sol 1980, 703 points, 556 segments) with the cards |

## What the AI did NOT do
- It did not download any data file (the AI session could not download PDS or Zenodo files), so file sizes and row counts in the cards are copied from web pages or marked as unknown.
- It did not write code for the project and did not touch the repository; VN created every file by hand in the GitHub web interface.
- It did not produce any validation number; all numbers in the cards are copied from the cited sources.

## Mistakes found and corrected
- An early draft of the Gale crater radiation card gave a dose equivalent of 0.67 mSv/day (from a press release). After reading the paper itself the card now uses 0.64 +/- 0.12 mSv/day.
- An early draft gave the Nature Geoscience MEDA paper year as 2022; the correct publication year is 2023.
- Early drafts mixed Opportunity and Gale values into the "Jezero" environment cards; after VN asked for Jezero-only values, every card now says where a value was measured and Jezero data were added.
- A claim from a second check list (Mendeley data set license "blank") was not used; the Mendeley page itself shows CC BY 4.0.

## Entries for 15 Nov
| Date | Who | Tool and model | What it was used for | Human check |
| --- | --- | --- | --- | --- |
| 2026-11-15 | VN | Claude (claude.ai, web search on) | Checked Carter et al. 2013, JMARS terms, CRISM TRDR DOI, MEDA and RAD license sources; drafted vn-crism-jmars.md and vn-env-licenses.md | VN opened the Carter 2013 paper and checked that it uses CRISM targeted observations, read the JMARS terms page (citation policy and privacy only), and checked the TRDR DOI 10.17189/1519573 and the PDS FAQ; all matched |
| 2026-11-15 | VN | Claude (claude.ai) | Helped word the "Human check" column of this log and explained what to verify in each source | VN wrote the final text of this log and confirmed each line against what was actually checked |


## Short paragraph for docs/SUBMISSION.md (AI tools used)
VN used Claude (Anthropic, claude.ai with web search) to find and summarize public sources about CRISM data, Mars radiation and dust, Jezero geology, the Perseverance traverse data and Jezero rock data, and to draft the research cards in docs/research/. Every claim in a card carries a source link, and where a source could not be checked the card says so. VN opened the cited source links and compared the key facts in each card with the pages, created and committed the files by hand, and tested the website in a browser. The AI did not write project code, did not download data, and did not produce any validation result.
