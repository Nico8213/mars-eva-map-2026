# Tasks: c-sync

- [x] 1. Write `tools/sync_to_web.py` (R1 to R5)
  - [x] 1.1 Paths, `copy_file` with size check and error handling
  - [x] 1.2 Folder, file and glob steps with missing-source notices
  - [x] 1.3 Route index writer
  - [x] 1.4 Summary lines and exit code
  - _Requirements: R1, R2, R3, R4, R5_

- [x] 2. Verify
  - [x] 2.1 Run in the repository with no source data: notices only, exit 0, nothing written
  - [x] 2.2 Run on a temporary tree with fake sources: all files copied, index written, summary printed
  - [x] 2.3 Remove one source and an overwrite check in the temporary tree
  - _Requirements: R1 to R5_

- [x] 3. Housekeeping
  - [x] 3.1 Add one line to `docs/ai_log/C-charles.md`
  - [x] 3.2 Commit with the `[C]` prefix in English
