# CI Investigation Report — twrp_j1minilte (Task 1.1)

Status: COMPLETE (2026-08-11). All three historical failures classified; fixes landed.

## Runs investigated (repo: trefeon/twrp_j1minilte)

### Run 31421309135 (oldest) — FAIL
- **Failing step:** `Set up job`
- **Root cause:** `Unable to resolve action pierotofy/set-swap-space@v1 — unable to find version 'v1'`
- **Classification:** dependency / tooling (third-party action removed/renamed)
- **Fix:** replace action with shell-based disk-aware swap setup (commits d039d6d2, c437f4d4)

### Run 31421517523 — FAIL
- **Failing step:** `Set swap space (dynamic, disk-aware)`
- **Root cause:** `fallocate failed: Text file busy` — GitHub runner images ship an already-active `/swapfile`; the first swap step version tried to fallocate over it without swapoff
- **Classification:** build environment (swap setup)
- **Fix:** swapoff + remove pre-existing `/swapfile` before creating ours (commit c437f4d4)

### Run 31421781959 — FAIL
- **Failing step:** `Sync TWRP sources (omni twrp-6.0)`
- **Root cause:** `cp: cannot create directory '/home/runner/TWRP/device/samsung/j1minilte': No such file or directory` — `repo init` does not create `device/samsung/`; the old workflow copied the device tree without `mkdir -p`
- **Classification:** checkout / layout
- **Fix:** full source relocation (device tree + kernel into AOSP-standard paths, commit 4908f45a) + workflow copies from this repo with explicit `mkdir -p` for both `device/samsung` and `kernel/samsung`

### Run 31465251155 (first run of the relocated workflow) — FAIL
- **Failing step:** `Build TWRP`
- **Root cause:** Python 3 SyntaxErrors (`Missing parentheses in call to 'print'`, `except IOError, ES.ParseError`) — omni twrp-6.0 build scripts require **Python 2**; ubuntu-22.04 ships only python3
- **Classification:** build environment (legacy interpreter missing)
- **Fix:** install `python2` from the `jxu/python2` PPA, symlink `python -> python2` (commit e92c2bf2)

## Runner environment (ubuntu-22.04, from run logs)
- JDK: Zulu 8 (0.502-7) via actions/setup-java
- Repo tool: `~/.bin/repo` (git-repo-downloads)
- Swap: 12 GB dynamic, disk-aware
- Toolchain: arm-eabi-4.8 @ android-5.1.1_r38 (googlesource, LineageOS mirror fallback)

## Verification method
`gh run view <run-id> --log-failed` — earliest actionable error captured for each run; no guessed fixes (each change was made only after observing the specific error).

## Next
- Await run triggered by e92c2bf2; iterate on any further observed failures.
- After first clean build: pin manifest revision, add size-check + checksums + metadata (FR-3), then device test.
