# AI log: Nico (N)

Role: repository manager, rules and submission, routing and validation specification, merging and checking pull requests.
Rule used with every AI tool: do not invent numbers; every number needs a source; unknown values stay marked as unknown until read from a real file.

| Date | Tool | Task | Result | How it was checked |
| --- | --- | --- | --- | --- |
| 2026-11-14 | Claude (chat) | Drafted the validation details of the routing specification: tolerance and verdict thresholds, coordinate system and distance rule, unreachable and blocked-cell rules, the meaning of the first and last reference point | `docs/research/nico-routing-spec.md` | Values that needed real files were left unknown until Austin read them from the files; the parameters were locked by Austin in commit d1965fd before any comparison was run |
| 2026-11-14 | Claude (chat, web search) | Looked up the USGS product pages, the PDS statements and the Space Apps rules to compare licenses of the HiRISE DTM, the CTX mosaic and CRISM data | `docs/research/nico-crism-license-check.md` and license wording in `docs/CITATIONS.md` | Compared with VN's research cards; the CTX license was corrected after Xin En showed the USGS data release page |
| 2026-11-14 to 2026-11-15 | Claude (chat) | Drafted and revised `docs/CITATIONS.md` and `docs/INTERFACES.md` from the team's research cards and Kiro search results | Files committed by Nico | Field names in INTERFACES were corrected against the real `grid.json` field list; rows without a source were left as unknown |
| 2026-11-14 to 2026-11-15 | Claude (chat) | Explained how to check and merge pull requests, and how to fix the failed GitHub Pages deploy | Split of the deploy workflow into build and deploy jobs (run #46 passed) | Checked in the GitHub Actions list |
| 2026-11-14 to 2026-11-15 | Kiro (Haiku 5.5, read-only prompts) | Searched the repository for PRD, TBD, version strings, large files, coordinate-conversion code, requirements, licenses and Chinese text | Lists of file names and line numbers; no file was changed by these prompts | Results were read by Nico and sent to the file owners |
| 2026-11-15 | Kiro (on Nico's account) | Prepared the documentation pull requests #56 (reproduction steps, citations, removal of two outdated documents) and #57 (a README sentence on the scope of the validation comparison) | Merged by Nico | Files changed were checked before merging |
| 2026-11-15 | Claude (chat) | Checked the final demo video frame by frame (labels, claims, web address) and added on-screen AI labels and the web address with ffmpeg | A labelled copy of the video | Frames were extracted and viewed after the change |
| 2026-11-15 | Claude (chat) | Reviewed and corrected the English of the project page text | Final project page text | Each claim was compared with the repository, the data cards and `validation/out/report.json` |

