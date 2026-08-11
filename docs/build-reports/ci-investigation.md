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

### Run 31465742633 (python2 via jxu PPA) — FAIL
- **Failing step:** `Install legacy Python 2 (AOSP 6.0 build scripts require it)`
- **Root cause:** `ERROR: ppa 'jxu/python2' not found` — the PPA has been removed upstream. Deadsnakes does not build python2 for jammy+ ("older python versions require libssl<3 so they are not currently built", per deadsnakes Launchpad, verified 2026-08-11).
- **Classification:** build environment (no packaged python2 for ubuntu-22.04 exists in 2026)
- **Fix:** build Python 2.7.18 from source (python.org tarball, `--prefix=/usr/local/python2.7`, symlink `python`/`python2`) — commit 20468788. zlib/bz2 modules build from the AOSP dev packages already installed.

### Run 31466528272 (python2 from source) — FAIL
- **Failing step:** `Build TWRP`
- **Root cause:** `prebuilts/clang/linux-x86/host/3.6/bin/clang: error while loading shared libraries: libncurses.so.5` — the omni-6.0 tree's bundled host clang 3.6 links against legacy ncurses5; ubuntu-22.04 default is ncurses6. (Confirmed: `libncurses5`/`libtinfo5` exist as jammy universe packages, 6.3-2ubuntu0.2.)
- **Classification:** build environment (legacy shared library)
- **Fix:** add `libncurses5 libtinfo5` to the AOSP host deps (commit 73dcfaeb)

### Run 31466973967 (libncurses5) — FAIL
- **Failing step:** `Build TWRP` → kernel `headers_install`
- **Root cause:** `Makefile.headersinst:55: *** Missing UAPI file include/uapi/linux/netfilter/xt_CONNMARK.h. Stop.` — the upstream kernel tree contains case-variant filename pairs (`xt_CONNMARK.h`/`xt_connmark.h` …); a case-insensitive Windows checkout keeps only one disk file per pair, so 12 exact-case paths were absent from the committed tree.
- **Classification:** source tree (case-collision loss)
- **Fix:** restored all 12 exact-case entries (8 netfilter uapi headers + 4 netfilter module sources) from upstream blobs (commit dfccd4fb). Full-tree verification: all 45,073 upstream paths present exact-case; remaining blob diffs vs upstream are EOL-only (upstream committed CRLF, repo stores LF).

## Runner environment (ubuntu-22.04, from run logs)
- JDK: Zulu 8 (0.502-7) via actions/setup-java
- Repo tool: `~/.bin/repo` (git-repo-downloads)
- Swap: 12 GB dynamic, disk-aware
- Toolchain: arm-eabi-4.8 @ android-5.1.1_r38 (googlesource, LineageOS mirror fallback)

## Verification method
`gh run view <run-id> --log-failed` — earliest actionable error captured for each run; no guessed fixes (each change was made only after observing the specific error).

## Next
- Await run triggered by dfccd4fb (case-variant headers); iterate on any further observed failures.
- After first clean build: pin manifest revision, add size-check + checksums + metadata (FR-3), then device test.
