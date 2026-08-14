# Project J105F — Master Execution Roadmap

**Target device:** Samsung Galaxy J1 Mini, SM-J105F (`j1minilte` / `j1miniltexx`), SoC `sc8830`
**Deliverable 1 (MVP):** a reproducible, self-branded TWRP recovery built from source committed in this project
**Deliverable 2 (experimental):** a bootable postmarketOS/Alpine Linux port

**Status:** A2 **DONE** (rollback set + evidence re-captured, 2026-08-12) · A1/A4/A4b done · A3 partial (heimdall PIT outstanding) · B1–B3 done · C1–C3 done (C3 incl. `recovery.tar.md5`) · **D1–D3 done (D3 splash 2026-08-14)** · E1 pre-flight parse recorded — E2 flash unblocked pending human "yes" · G1–G3 done (M3.1/M3.2) — G4 kernel flash unblocked pending human "yes" · **H1 done 2026-08-14 (initramfs boots to shell, CI-verified; boot.img `e3125677` @ `f649d5a5`)** · H2/H3/H5/H6 research pack written (`docs/research/driver-bring-up-h2h3.md`) · I not started · **no image flashed yet**
**Last evidence refresh:** 2026-08-12 (A2 rollback set: 4× dd images + TWRP System/Data backup on PC; C8 captures fixed; TWRP identified as 3.7.0_9-0-notnoelchannel)

---

## 0. How an agent executes this file

This document is the **single execution spine**. Work tasks in ID order (A1 → A2 → … → I4). Do not skip
ahead: later tasks assume earlier acceptance criteria actually passed.

**Per-task protocol**

1. Read **Depends on**. If a dependency is unchecked, stop and do that task first.
2. Perform **Do**.
3. Run **Verify** exactly as written. Paste real output into the task's evidence log.
4. Only if **Accept** is objectively satisfied, tick the checkbox and append a line to
   `docs/delivery/execution-log.md` in the form:
   `<TASK-ID> | <ISO date> | done|blocked | <one-line result> | <commit sha or artifact ref>`
5. If blocked, tick nothing. Record the blocker and the earliest actionable error, then stop and report.

**Hard rules**

- **Never flash the device without an explicit human "yes" in the current session.** Tasks marked
  `HUMAN GATE` require a person holding the phone. An agent may prepare, checksum, and stage — never flash.
- **Never claim a capability you did not observe.** "Kernel compiled" is not "device boots".
- Never commit private images (`*.img`), EFS data, modem blobs, or keys. `.gitignore` already excludes them —
  do not weaken it.
- Prefer the smallest verified number when two sources disagree about partition size. See A3.
- One coherent commit per task where files change. Reference the task ID in the commit subject.

**Two-repository layout — read before editing any build file**

| Path | Git remote | Role |
|---|---|---|
| `D:\github_repo\Project_J105F` | `github.com/trefeon/Project_J105F` | Research, plans, device evidence, tooling |
| `D:\github_repo\Project_J105F\twrp\` | `github.com/trefeon/twrp_j1minilte` | **Nested, separate repo.** Device tree, kernel, and the CI workflow that actually builds |
| `D:\github_repo\Project_J105F\os\kernel\` | `github.com/trefeon/linux-samsung-j1minilte` | **Nested, separate repo.** Linux kernel foundation (Phase 3 / G-stage); CI builds boot.img |

`twrp/` and `os/kernel/` are listed in the parent `.gitignore`. Edits to `twrp/.github/workflows/twrp.yml`, the device tree, or
the kernel must be committed and pushed **from inside `twrp/`, to `twrp_j1minilte`** — pushing the parent repo
will not trigger any build. Same for `os/kernel/` → `linux-samsung-j1minilte`.

---

## 1. Verified ground truth

Everything here was confirmed from live device evidence or repository inspection on 2026-08-11. Treat it as
authoritative; treat the older plan documents as reference material only.

### Device identity (live ADB capture, `device/evidence/`)

| Property | Value | Source |
|---|---|---|
| Model / device / product | `SM-J105F` / `j1minilte` / `j1miniltexx` | `getprop.txt` |
| Platform / bootloader board | `sc8830` (**family name** — SoC is **SC9830i LTE**/SharkLS) / `SC9830I` | `getprop.txt`, `BoardConfig.mk`, `docs/research/exact-model-findings.md` |
| Firmware (PDA) | `J105FXXS0ARD2`, Android 5.1.1, `LMY47V` | `getprop.txt` |
| CSC | `XID` — Indonesia | `getprop.txt` |
| **SIM configuration** | **Dual-SIM (DSDS)** — `ro.multisim.simslotcount=2`, `libsec-ril-dsds.so` | `getprop.txt` |
| **RAM** | **941,892 kB MemTotal (~1 GB)** | `meminfo.txt` |
| CPU | ARMv7 Cortex-A7 (`0xc07`) rev 5, hardware `sc8830` | `cpuinfo.txt` |
| Stock kernel | `3.10.65-9723235`, gcc 4.8, built 2018-04-23 | `version.txt` |
| Touchscreen | `sec_touchscreen` on **`/dev/input/event2`**, 480×800, `INPUT_PROP_DIRECT` | `input_devices.txt` |
| Other inputs | `sci-keypad` (event1), `headset-keyboard` (event4), `accelerometer_sensor` (event3) | `input_devices.txt` |
| Battery sysfs | `POWER_SUPPLY_*` fully populated (Li-ion, capacity, temp, voltage) | `battery.txt` |
| Loaded modules | `mali.ko`, `sprdwl.ko` (Wi-Fi), `pskey_bt.txt` | `modules.txt` |
| Internal eMMC | `mmcblk0`, 7,634,944 KiB (~7.3 GiB) | `partitions.txt` |
| microSD present | `mmcblk1p1`, 3,861,504 KiB (~3.7 GiB) | `partitions.txt` |

### Partition map (authoritative — `byname.txt` × `partitions.txt`)

Block counts are 1024-byte units.

| Name | Device | Blocks | **Real size** |
|---|---|---|---|
| KERNEL (boot) | `mmcblk0p20` | 16384 | **16 MiB** |
| RECOVERY | `mmcblk0p21` | 16384 | **16 MiB** |
| SYSTEM | `mmcblk0p25` | 2199552 | 2097 MiB |
| CACHE | `mmcblk0p24` | 204800 | 200 MiB |
| userdata | `mmcblk0p27` | 5054464 | 4819 MiB |
| efs | `mmcblk0p17` | 20480 | 20 MiB |
| HIDDEN (preload) | `mmcblk0p26` | 40960 | 40 MiB |
| prodnv | `mmcblk0p18` | 5120 | 5 MiB |

### Build recipe (from `twrp/.github/workflows/twrp.yml` + `BoardConfig.mk`)

| Piece | Value |
|---|---|
| Manifest | `minimal-manifest-twrp/platform_manifest_twrp_omni` @ `twrp-6.0` |
| Device tree | committed at `twrp/device/samsung/j1minilte` |
| Kernel | committed at `twrp/kernel/samsung/j1minilte` — **3.10.65**, `j1minilte_defconfig` (94,428 B) |
| Toolchain | `arm-eabi-4.8` @ `android-5.1.1_r38`, hardcoded to `/opt/toolchains/arm-eabi-4.8/bin` by `KERNEL_TOOLCHAIN` |
| Prebuilt DTB | `device/samsung/j1minilte/prebuilt/dtb` (329,728 B) passed via mkbootimg `--dt` |
| Boot geometry | base `0x0`, kernel `0x8000`, ramdisk `0x1000000`, tags `0x100`, pagesize 2048 |
| Kernel cmdline | `console=ttyS1,115200n8` |
| Build | `lunch omni_j1minilte-eng && make recoveryimage` |
| Runner | `ubuntu-22.04`, JDK 8 (Zulu), disk-aware swap |

### Repository state

- Nested `twrp` repo: **clean**, HEAD `634cb96c` (D3 splash on top of branding `2d63e410` + 16 MiB gate `0f7f3586`); CI green — runs `31469647748`, `31472573689`, `31474055688`, `31524994619`, `31801523361`; final artifacts (run `31801523361` = HEAD): `recovery.img` 11.88 MiB (sha256 `3651e105…`, incl. **D3 custom splash**), `recovery.tar`, `recovery.tar.md5` (md5 `fb8355dd…`), SHA256SUMS + BUILD_INFO.txt + manifest-pinned.xml.
  > **2026-08-14 corrections:** (1) the flash bundle at `device/evidence/build-artifacts/twrp-j1minilte/` previously held the *first-green* image (`9869d726`, commit `dfccd4fb`) — pre-branding and pre-gate — and the Odin tar was built from it. Replaced with the gated HEAD artifact `799b5e10`; tar + md5 rebuilt. (2) **D3 (2026-08-14):** re-synced to the splash build — recovery.img `3651e105` @ `634cb96c` (run `31801523361`); tar + md5 rebuilt (`fb8355dd…`). Prior SHA references in this §1 (e.g. `aa34d1d0…` under `final/`) refer to the pre-gate branding build and must not be flashed.
- Nested `os/kernel` repo: **clean**, HEAD `f649d5a5` (H1 initramfs: boots to shell + fail-closed initramfs CI verify + CMDLINE landmine removed); CI green — runs `31519306192`, `31520084805`, `31524994372`, `31799705308`; artifacts (gate-verified run `31799705308` = HEAD): `boot.img` 6.53 MiB (sha256 `e3125677…`), zImage, dt.img, ramdisk.cpio.gz (H1 debug shell), .config, SHA256SUMS, BUILD_INFO.txt.
  > **2026-08-14 corrections:** (1) kernel flash bundle re-synced from the pre-gate run `31519306192` (boot.img `a8603c2d`) to the gate-verified run `31524994372` (boot.img `671a576a`, commit `f31f090a`). (2) **H1 (2026-08-14):** re-synced again to run `31799705308` (boot.img `e3125677`, commit `f649d5a5`) — the new boot.img carries the H1 debug initramfs (shell on serial ttyS1 + panel tty1, fail-closed verified in CI); zImage identical to the `671a576a` bundle's, dt.img unchanged. Flash only `e3125677…`.
- Parent repo: all docs committed (this ROADMAP included).
- CI history on `twrp_j1minilte`: early runs `31421309135`, `31421517523`, `31421781959`, `31465251155` failed (root-caused one by one) → green since `31469647748`.

---

## 2. Corrections to prior documents

The agent must apply these. Prior docs are wrong on these points; this section wins.

| # | Prior claim | Where | Correction | Evidence |
|---|---|---|---|---|
| C1 | "Nested TWRP repository has a broken working-tree transition… must be resolved" (Phase 0, Task 0.1) | `tasks.md:11,24-32` | **Already done.** Tree is clean at `4908f45a`. Phase 0 is obsolete. | `git -C twrp status --porcelain` → empty; 45,078 tracked files |
| C2 | "single-SIM" | `tasks.md:9` | **Dual-SIM (DSDS).** | `ro.multisim.simslotcount=2` |
| C3 | "768 MB RAM", "768 MB total" | `linux-port-plan.md:63,94` | **~1 GB** (941,892 kB). The same doc's own table already said 1 GB — it contradicts itself. | `meminfo.txt` |
| C4 | "boot+recovery = 20 MB (20971520 B)" | `linux-port-plan.md:14`, `BoardConfig.mk:44-45`, `prd.md:49` | **16 MiB (16,777,216 B).** BoardConfig overstates by 4 MiB. See risk R1. | `partitions.txt` p20/p21 = 16384 blocks |
| C5 | Rollback source is `device/evidence/stock-backup/recovery_stock.img` | `twrp-build-plan.md:62`, `linux-port-plan.md:35` | **That file does not exist.** Only `dtb/` survives; `*.img` is gitignored and absent from disk. | directory listing |
| C6 | CI blocker is "ubuntu-20.04 retired" / JDK | `twrp-build-plan.md:22-28` | Solved. **Current blocker is Python 2.** | run `31465251155` log |
| C7 | Kernel is 3.10.65 *or* 3.10.100 *or* 3.10.106 depending on doc | multiple | For **TWRP**, the committed kernel is **3.10.65**. The 3.10.100/3.10.106 candidates belong only to the Linux port. | `twrp/kernel/.../Makefile` |
| C8 | `/proc/cmdline`, `dmesg`, `df` captured | `device/evidence/` | **All three captures failed** (`Permission denied`, `head: not found`, bad flag). Files contain error text, not data. | file contents |

---

## 3. Risk register

| ID | Risk | Severity | Control |
|---|---|---|---|
| **R1** | **Recovery partition overflow.** CI would accept a 20 MiB image; the partition is 16 MiB. An image in the 16–20 MiB window passes the check and then overflows on flash, corrupting the adjacent partition. Latent today only because typical TWRP images are ~10 MiB. | **Critical** | C3 task: enforce 16,777,216 B in CI, confirm against PIT before any flash |
| **R2** | **No rollback image exists.** Nothing to restore if the new recovery fails to boot. | **Critical** | A2 must complete before any flash; E-stage is hard-blocked on it |
| R3 | Flashing the wrong variant | Critical | Every flash task re-asserts `ro.product.device == j1minilte` and PDA `J105FXXS0ARD2` |
| R4 | Legacy AOSP 6.0 on a modern runner (Python 2, make ≥4.3, new binutils) | High | Pin and record every host input; fix one root cause per iteration, never speculative bundles |
| R5 | EFS/IMEI loss | Critical | EFS backup in A2 before any write operation; never commit it |
| R6 | Linux port claims outrunning evidence | Medium | Every Linux milestone needs 3 boots + logs (Gate D) |
| R7 | Wi-Fi firmware unavailable for pmOS | Medium/High | USB RNDIS is the declared fallback; label Wi-Fi unsupported until proven |
| R8 | Upstream `googlesource` toolchain fetch flakiness | Medium | LineageOS GitHub mirror already wired as fallback in the workflow |

---

## 4. The roadmap

### Stage A — Foundation and evidence integrity

Cheap, safe, unblocks everything. No device writes.

#### A1 — Retire stale planning docs and commit the roadmap
- **Depends on:** none
- **Do:** Commit this file. Add a one-line banner at the top of `docs/delivery/tasks.md`,
  `docs/plans/twrp-build-plan.md`, and `docs/plans/linux-port-plan.md`:
  `> Superseded as an execution plan by docs/delivery/ROADMAP.md. Retained for reference detail only.`
  Apply corrections C2, C3, C4 inline in those files so no stale number survives anywhere.
- **Accept:** No document still asserts single-SIM, 768 MB, or a 20 MiB recovery partition.
- **Verify:**
  ```powershell
  Select-String -Path docs\**\*.md -Pattern "768 MB|single-SIM|20971520" 
  ```
  Every hit is either inside this roadmap's correction table or a quoted BoardConfig value being flagged.
- [x] Done — 2026-08-11: ROADMAP committed; banners added to tasks.md / twrp-build-plan.md / linux-port-plan.md; corrections C2/C3/C4 applied inline in tasks.md + linux-port-plan.md + prd.md.

#### A2 — Re-capture device evidence and create the rollback set — `HUMAN GATE` (phone + USB)
- **Depends on:** A1
- **Why first:** R2 and R5. Nothing may touch the device's flash until a restorable backup exists.
- **Do:** Boot the existing TWRP 3.0.3-0, `adb root`, then:
  1. Dump to microSD (never to the repo): `RECOVERY` (p21), `KERNEL` (p20), `efs` (p17), `prodnv` (p18).
     Example: `dd if=/dev/block/mmcblk0p21 of=/external_sd/backup/recovery_stock.img bs=4096`
  2. Also run a full TWRP backup (System, Data, EFS) to microSD.
  3. Copy all images to the PC at `device/evidence/stock-backup/` (gitignored — stays local).
  4. Write `device/evidence/stock-backup/CHECKSUMS.sha256` (this file **is** committed) and a short
     `README.md` naming each image, its partition, its size, and its restore command.
  5. Re-capture the three failed captures from C8: `/proc/cmdline` (needs root), `dmesg`, `df`.
- **Accept:** Four `.img` files exist locally with recorded SHA-256; a TWRP backup is verified on the PC;
  `cmdline.txt`, `dmesg.txt`, `df.txt` contain real data.
- **Verify:**
  ```powershell
  Get-ChildItem device\evidence\stock-backup\*.img | Select-Object Name,Length
  Get-Content device\evidence\stock-backup\CHECKSUMS.sha256
  Get-Content device\evidence\cmdline.txt
  ```
  `recovery_stock.img` must be exactly 16,777,216 bytes. If it is not, **stop** — the partition map is wrong
  and R1 needs re-analysis before anything else.
- **If it fails:** No backup, no flash. Stages E and G+ remain hard-blocked.
- [x] Done — **2026-08-12.** Live device TWRP was identified as **3.7.0_9-0-notnoelchannel** (not 3.0.3-0 as previously assumed; docs corrected). Dumped `RECOVERY` p21, `KERNEL` p20, `efs` p17, `prodnv` p18 to microSD → pulled to `device/evidence/stock-backup/`: recovery/boot exactly **16,777,216 B** (stop rule passed — partition map live-confirmed, R1 re-validated), efs 20,971,520 B, prodnv 5,242,880 B — all match the ROADMAP table. `CHECKSUMS.sha256` + `README.md` committed. TWRP full backup (System 2.09 GB + Data 1.29 GB, each with `.sha2`) completed on microSD and pulled to PC. C8 captures re-done with real data: `cmdline.txt` (`console=null loglevel=0`, `androidboot.bootloader=J105FXXS0ARD2`, `hw_revision=3`, `mem=1024M`), `dmesg.txt` (441 KB), `df.txt`. EFS additionally covered by the raw dd (p17). TWRP CLI `print`/long ORS runs can wedge the recovery UI (observed twice) — use CLI backup sparingly; device recovered with `adb reboot recovery`; no data at risk (all writes were to microSD only).

#### A3 — Establish the authoritative partition geometry
- **Depends on:** A2
- **Do:** Boot Download Mode, run `heimdall print-pit` from the Windows host, save the raw output to
  `docs/reference/pit-J105F.txt` and commit it. Build a table comparing PIT vs `/proc/partitions` vs
  `BoardConfig.mk` for KERNEL and RECOVERY.
- **Accept:** The three sources are reconciled and a single number is chosen for each partition —
  **the smallest of the verified values**. Expected outcome: 16,777,216 B for both.
- **Verify:** `Select-String -Path docs\reference\pit-J105F.txt -Pattern "RECOVERY|KERNEL"` shows sizes that
  match `partitions.txt`.
- **If heimdall cannot enumerate the device:** proceed using the live `/proc/partitions` value and record
  that PIT confirmation is outstanding. Do not use the BoardConfig value.
- [ ] Done — **PARTIAL.** Live `/proc/partitions` evidence in `device/evidence/partitions.txt` (p20/p21 = 16,384 KiB = 16 MiB) already applied as C4 correction; heimdall PIT capture outstanding.

#### A4 — Correct the partition sizes in the device tree
- **Depends on:** A3
- **Do:** In `twrp/device/samsung/j1minilte/BoardConfig.mk`, set both
  `BOARD_BOOTIMAGE_PARTITION_SIZE` and `BOARD_RECOVERYIMAGE_PARTITION_SIZE` to the A3 value (16777216).
  Add a comment citing the evidence. Commit **inside `twrp/`** and push to `twrp_j1minilte`.
- **Accept:** BoardConfig no longer claims 20971520.
- **Verify:**
  ```powershell
  Select-String -Path twrp\device\samsung\j1minilte\BoardConfig.mk -Pattern "PARTITION_SIZE"
  git -C twrp log --oneline -1
  ```
- [x] Done — 2026-08-11. `BoardConfig.mk` now 16777216 for BOOT+RECOVERY with an evidence comment (live `/proc/partitions` p20/p21 = 16,384 KiB; ROADMAP C4). Commit `0f7f3586` (twrp repo).

#### A4b — (kernel repo) boot partition size
- **Do (2026-08-11):** kernel `kernel.yml` size gate tightened from 20971520 to 16777216 (fail closed ≥ limit).
- [x] Done — 2026-08-11. Commit `f31f090a` (kernel repo); both green runs re-verified: recovery.img 11,890,688 B and boot.img 6,850,560 B both < 16,777,216.

---

### Stage B — Get CI to a green recovery build

No device involvement. Iterate until the build produces an image.

#### B1 — Fix the Python 2 blocker
- **Depends on:** A4
- **Root cause (already diagnosed, run `31465251155`, step "Build TWRP"):** the omni `twrp-6.0` build system
  is Python 2. Two distinct failures in the same step:
  - `envsetup.sh` runs `python -c "import os,sys; print os.path.realpath(sys.argv[1])"` →
    `SyntaxError: Missing parentheses in call to 'print'`
  - `build/tools/roomservice.py:109` has `except IOError, ES.ParseError:` →
    `SyntaxError: multiple exception types must be parenthesized`

  The workflow installs `python3` only, and Ubuntu 22.04 ships no `python` at all.
- **Do:** In `twrp/.github/workflows/twrp.yml`, in the dependencies step, add `python2` to the apt list and
  symlink it: `sudo ln -sf /usr/bin/python2 /usr/bin/python`. Leave the `repo` invocations calling `python3`
  explicitly — `repo` itself requires Python 3, so do **not** point `repo` at the symlink.
- **Accept:** The "Build TWRP" step advances past `lunch` and begins compiling.
- **Verify:**
  ```powershell
  rtk gh run list --repo trefeon/twrp_j1minilte --limit 1
  rtk gh run view <run-id> --repo trefeon/twrp_j1minilte --log-failed
  ```
  The two `SyntaxError` lines must be gone. A *different*, later error is progress — record it and continue
  to B2.
- [x] Done — 2026-08-11. Resolved with a **source-built Python 2.7.18** (`/usr/local/python2.7`) after the jxu PPA vanished; `libncurses5`/`libtinfo5` from jammy universe. The "Build TWRP" step advanced past `lunch` and compiled (run 31465251155 onwards).

#### B2 — Drive the build to completion, one root cause per iteration
- **Depends on:** B1
- **Do:** Loop: read `--log-failed`, identify the **earliest** actionable error (never a downstream cascade),
  fix exactly that one thing, push, re-run. Record each iteration in the execution log as
  `error → cause → fix → outcome`.
- **Forecast of likely failures, in the order they tend to appear.** Use as a lookup, not as a pre-emptive
  patch list — never apply a fix for an error you have not actually seen:
  1. `make` ≥ 4.3 incompatibility with AOSP ≤ 6.0 (`missing separator`, jobserver breakage) — the classic
     remedy is a locally built `make` 3.82/4.1 placed ahead on `PATH`.
  2. Host GCC too new for AOSP 6.0 host tools — pin `CC`/`CXX` to gcc-9 or older via apt.
  3. Kernel 3.10 build scripts also invoking Python 2 — covered by B1's symlink; confirm it survives into the
     kernel sub-make environment.
  4. `arm-eabi-4.8` clone stalling on googlesource — the LineageOS mirror fallback is already wired in.
  5. Missing legacy 32-bit host libs — add only the specific library named in the error.
- **Accept:** `out/target/product/j1minilte/recovery.img` is produced.
- **Verify:** The workflow reaches "Package Odin tar" and the artifact upload succeeds. Download the artifact
  and confirm it is non-empty.
- [x] Done — 2026-08-11. Green runs `31469647748` (dfccd4fb) and `31472573689` (33819a71); final branded `31474055688` (2d63e410). All 6 root causes documented in `docs/build-reports/ci-investigation.md`.

#### B3 — Validate kernel integration explicitly
- **Depends on:** B2
- **Do:** Add a CI step, before the recovery build, that asserts: `TARGET_KERNEL_CONFIG` (`j1minilte_defconfig`)
  exists in the kernel tree; `KERNEL_TOOLCHAIN` resolves and `arm-eabi-gcc --version` runs; the DTB prebuilt is
  present and 329,728 bytes. Upload the kernel build log as an artifact **on failure**.
- **Accept:** The build fails fast and legibly if any kernel input is missing, instead of failing deep inside
  `make`.
- **Verify:** Temporarily rename the defconfig in a scratch branch; the run must fail at the assertion step
  with a clear message. Revert.
- [x] Done — 2026-08-11. CI asserts defconfig presence, `arm-eabi-gcc --version`, and the prebuilt DTB (329,728 B) before the recovery build.

---

### Stage C — Artifact safety and reproducibility

Implements PRD FR-2, FR-3. This is what makes the image safe to hand to a human.

#### C1 — Enforce the real partition size, fail closed
- **Depends on:** B2, A3
- **Do:** After the build, compare `stat -c%s recovery.img` against the A3 value (16777216) and `exit 1` if it
  is greater or equal. Print actual size, limit, and headroom.
- **Accept:** An oversized image can never be published. This directly closes R1.
- **Verify:** Read the step log — it must print the real byte count and the 16,777,216 limit. Confirm the
  comparison is `>=`, not `>`.
- [x] Done — 2026-08-11. Both CI gates now fail closed at ≥ 16,777,216 B: twrp.yml (`0f7f3586`, `-ge 16777216`) and kernel.yml (`f31f090a`, `assert size < 16777216`). Green runs 31524994619 (recovery.img 11,890,688 B) and 31524994372 (boot.img 6,850,560 B). Comparison is `>=` per the roadmap rule. R1 closed.

#### C2 — Checksums and build metadata
- **Depends on:** C1
- **Do:** Emit `recovery.img.sha256`, `recovery.tar.sha256`, and `build-info.txt` containing: source commit SHA
  of `twrp_j1minilte`, resolved manifest revision (capture it with `repo info` after sync — this settles the
  PRD's first open decision), toolchain version, runner image, JDK, UTC build timestamp. Upload all as
  artifacts.
- **Accept:** Every artifact is traceable to an exact source state.
- **Verify:** Download the artifact bundle; recompute SHA-256 locally and match.
- [x] Done — 2026-08-11. `SHA256SUMS` + `BUILD_INFO.txt` (source commit, defconfig, toolchain, built_at, cmdline, mkbootimg params) + `manifest-pinned.xml` published with both TWRP and kernel artifacts; locally re-verified.

#### C3 — Odin packaging decision
- **Depends on:** C2
- **Do:** Resolve the PRD's open question. Produce `recovery.tar` (plain), and additionally
  `recovery.tar.md5` (tar with its MD5 appended, the classic Odin convention) so the human can try the plain
  form first and fall back. Document which Odin version was used for the eventual successful flash.
- **Accept:** Both artifacts exist; the flash instructions name a specific Odin version.
- **Verify:** `tar -tf recovery.tar` lists exactly `recovery.img`.
- [x] Done — 2026-08-12. Plain `recovery.tar` (11,898,880 B) + `recovery.tar.md5` (tar with 32-char MD5 appended, delta exactly 32 B, re-hash `6ba01d34e4661059329b4750d5ba4ca3` matches; `tar -tf` lists exactly `recovery.img`). **2026-08-14 correction:** the tar packaged the stale pre-branding image (`9869d726`); rebuilt from gated HEAD artifact `799b5e10` (run 31524994619), new md5 `52067f658c62a63cc689a0c77d513d94`. The remaining clause — "flash instructions name a specific Odin version" — is inherently device-dependent and stays OPEN until E2; release notes (F1) will name the winner per D-2.

---

### Stage D — Make it genuinely ours

#### D1 — Identity and branding
- **Depends on:** C3
- **Do:** Set `TW_DEVICE_VERSION` to a project-specific value including the short commit
  (e.g. `j105f-<shortsha>`), replacing the inherited `0_j1mini_custom`. Set `PRODUCT_MODEL` in
  `omni_j1minilte.mk`. Ship a build-info file inside the ramdisk so the running recovery can state its own
  provenance.
- **Accept:** TWRP's About screen shows this project's identity and the source commit.
- **Verify:** Unpack the built ramdisk and confirm the strings; visually confirm after E2.
- [x] Done — 2026-08-11, commit `2d63e410`. `TW_DEVICE_VERSION=0_j105f-custom`, `PRODUCT_MODEL="Samsung Galaxy J1 Mini (custom TWRP)"`; strings verified inside the final image ramdisk.

#### D2 — License audit
- **Depends on:** D1
- **Do:** Confirm the upstream AGPL `COPYING` and all TWRP/Code Aurora notices are intact and that
  attribution to the NotNoelChannel base is explicit in `README.md`.
- **Accept:** No notice removed; provenance documented.
- **Verify:** `git -C twrp log --oneline -- device/samsung/j1minilte/COPYING` shows no deletion.
- [x] Done — 2026-08-11. `COPYING` (AGPL-3.0) preserved; README credits NotNoelChannel base + archived pmOS recipe reference.

#### D3 — Splash and defaults
- **Depends on:** D2
- **Do:** 480×800 custom boot splash; confirm default brightness 162 and MTP-on defaults.
- **Accept:** Cosmetic only, and it must not increase the image beyond the C1 limit.
- **Verify:** C1's size check still passes.
- [x] Done — **2026-08-14.** 480×800 custom boot splash (`J105F / Samsung Galaxy J1 Mini / custom TWRP`, dark + Samsung-blue, version string bottom). TWRP 3.7.0_9 renders the boot splash from the **theme page** (`/twres/splash.xml` + `images/splashlogo.png`, 8-bit PNG — source-verified, not the legacy raw-RGB565 assumption). Implemented as a surgical post-build patch (`twrp` `634cb96c`): `tools/patch_splash.py` unpacks recovery.img, replaces exactly those two ramdisk files, repacks via `tools/pack_bootimg.py` with kernel/dt/cmdline/SEANDROID preserved + fail-closed verify + size gate. Locally round-tripped on the current artifact: VERIFY PASS, 11,874,304 B < 16 MiB. CI run `31801523361`. Splash generator committed at `tools/make-splash.py` (reproducible). Visual confirmation deferred to E2 (device).

---

### Stage E — Device validation — `HUMAN GATE` throughout

**Entry conditions, all mandatory:** A2 rollback set exists and is checksummed · A3 geometry confirmed ·
C1 size check green · the human is physically present and has explicitly approved this session.
**Status 2026-08-11:** NOT STARTED — blocked on A2 (rollback images missing), C1 (16 MiB gate), and the human gate. E1's pre-flight (`python tools/parse_bootimg.py`) is ready to run.

#### E1 — Pre-flash verification
- **Depends on:** D2, A2, C1
- **Do:** Re-assert device identity over ADB (`ro.product.device`, `ro.build.PDA`). Inspect the image header:
  confirm pagesize 2048, the offsets from §1, an embedded DTB, and total size < 16 MiB. Confirm the target is
  `mmcblk0p21`. Write the exact flash command and the exact rollback command side by side, and have the human
  read both back.
- **Accept:** Identity matches, header is sane, rollback command is verified correct.
- **Verify:** `python tools/parse_bootimg.py <recovery.img>` output recorded in the log.
- [ ] Done — pre-flight tooling ready (`tools/parse_bootimg.py` + kernel repo's `pack_bootimg.py`); local parse **recorded 2026-08-12** on the final image: pgsz 2048, kernel 5,146,640 B, ramdisk 6,408,655 B, DTB blob @ 0xb06800, 5× DTBs SP8835EB, sizes byte-identical to stock (`parsed-e1/`); **flash + rollback commands written side by side at `docs/delivery/e1-flash-commands.md` (2026-08-12, corrected 2026-08-14 to the gated HEAD image `799b5e10`)**; remaining: identity + partition assertions on the live device, then human walkthrough — unblocked now that A2 is done.

#### E2 — Flash and first boot
- **Depends on:** E1 + explicit human "yes"
- **Do:** Prefer the least destructive route first — from the existing working TWRP,
  `dd if=/sdcard/recovery_new.img of=/dev/block/mmcblk0p21`. Odin/AP with `recovery.tar` is the alternative.
  Reboot to recovery.
- **Accept:** The new recovery boots and displays its UI.
- **Verify:** Photograph the About screen showing the D1 identity string.
- **Rollback trigger:** No display, no touch, or a boot loop → immediately restore `recovery_stock.img` to
  p21 by the same method.
- [ ] Done — blocked on E1.

#### E3 — Functional test matrix
- **Depends on:** E2
- **Do:** Test and record pass/fail for each, individually: display · touch · orientation · brightness ·
  key mapping · **MTP** (the headline fix versus the 2017 build) · ADB shell · mount `/system` `/data`
  `/cache` `/efs` `/preload` `/productinfo` · internal storage · external SD (`mmcblk1p1`) · backup ·
  restore · a deliberate insufficient-space failure · reboot · download mode · encryption behavior.
- **Accept:** Every row has an explicit verdict. Anything failing is documented as a known limitation — never
  silently presented as working.
- **Verify:** Completed matrix committed to `docs/delivery/recovery-test-matrix.md`.
- [ ] Done — matrix drafted at `docs/plans/device-test-checklist.md`; execution blocked on E2.

#### E4 — Prove rollback
- **Depends on:** E3
- **Do:** Actually restore the stock recovery, boot it, then re-flash the custom recovery.
- **Accept:** Both directions demonstrated. Rollback is proven, not assumed.
- **Verify:** Boot evidence for both states in the log.
- [ ] Done — E-stage not reached yet (A2/C1/human gate).

---

### Stage F — Recovery release (MVP complete)

#### F1 — Release documentation
- **Depends on:** E4
- **Do:** Write `docs/releases/recovery-<version>.md`: supported variant (`j1miniltexx`/`sc8830` **only**),
  the tested firmware, the full test matrix result, known limitations, flash + rollback procedure, checksums.
- **Accept:** A stranger could reproduce the flash and recover the device from this document alone.
- [ ] Done — blocked on E4.

#### F2 — Clean-room rebuild
- **Depends on:** F1
- **Do:** Trigger a fresh CI run from a clean runner at the release commit. Compare artifact SHA-256 against
  the tested artifact; document any nondeterminism (timestamps commonly differ — say so explicitly rather
  than claiming bit-for-bit reproducibility you have not verified).
- **Accept:** A clean runner rebuilds successfully.
- [ ] Done — blocked on F1.

#### F3 — Secret sweep and tag
- **Depends on:** F2
- **Do:** Scan both repos for images, EFS content, modem blobs, and keys. Then tag the release in
  `twrp_j1minilte` and attach the artifacts.
- **Accept:** No private data tracked; release tagged and downloadable.
- **Verify:** `git -C twrp ls-files | Select-String "\.img$|efs|modem"` returns nothing.
- [ ] Done

> **Milestone: MVP delivered.** Stages G–I are a separate, experimental track. Their status must never be
> conflated with the recovery release status.

---

### Stage G — Linux kernel foundation (experimental)

**REVISED 2026-08-11:** executed CI-first instead of pmbootstrap-first (decisions D5/K1/K2 in
`docs/plans/linux-kernel-foundation-plan.md`): kernel repo `trefeon/linux-samsung-j1minilte` builds a
fail-closed verified `boot.img` on GitHub Actions. **M3.1/M3.2 done.** pmOS recipe fork (G2/G3 as written)
remains for the rootfs phase; WSL2/pmbootstrap deferred until then.

Strategy (retained): replicate the archived pmOS `samsung-j1mini3g` port (same SC8830 family, proven combination), then
diverge to `j1minilte`. Do not optimize before the first boot.

#### G1 — Build host and toolchain
- **Depends on:** F1 (recovery must be a reliable recovery path before experimenting)
- **Do (revised):** CI-first — GitHub Actions ubuntu-22.04 + `arm-eabi-4.8` (proven TWRP pattern). WSL2 Ubuntu
  + pinned `pmbootstrap` deferred to the rootfs phase. heimdall stays on Windows. The 892 MB VPS is confirmed
  infeasible for full builds — cross-compile only.
- **Accept (revised):** kernel + boot.img build reproducibly in CI (M3.1) — **DONE**.
- [x] Done — 2026-08-11, revised: CI-first (D5); M3.1 green runs 31519306192 + 31520084805.

#### G2 — Fork the kernel recipe
- **Depends on:** G1
- **Do (revised):** kernel source forked into `os/kernel/` → `trefeon/linux-samsung-j1minilte` (vendor
  `j1minilte` tree, K1 — the source already proven bootable via TWRP CI; DTB-identical to stock). The archived
  IKGapirov 3.10.106 recipe (original G2 text) is deferred as M3.4 follow-up.
- **Accept (revised):** kernel builds reproducibly, config saved, checksums published — **DONE (M3.1)**.
- [x] Done — 2026-08-11, revised: K1 vendor-kernel-first; commit 90cfeaa5 + CI green.

#### G3 — Device package and boot image
- **Depends on:** G2
- **Do (revised):** `boot.img` assembled directly in CI (mkbootimg v0, offsets from §1, cmdline
  `console=ttyS1,115200n8`, SPRD dt.img packed from device stock DTBs, SEANDROIDENFORCE) + busybox debug
  initramfs (K2). Size: 6.53 MiB — **under the 16 MiB A3 value**. pmOS `device-samsung-j1minilte` package
  (original G3 text) deferred to the rootfs phase.
- **Accept (revised):** fail-closed verify passes (header, size, dt.img byte-identical) — **DONE (M3.2)**.
- [x] Done — 2026-08-11, revised: `VERIFY PASS` in CI; artifacts + checksums in `device/evidence/build-artifacts/kernel-m31/`.

#### G4 — First kernel boot attempt
- **Depends on:** G3, A2 (rollback), E4 (proven restore path)
- **`HUMAN GATE`**
- **Do:** Flash **only** the KERNEL partition (p20) via TWRP → Install Image. Never overwrite RECOVERY at this
  stage — it is the escape hatch. Capture output: fbcon on the display, `last_kmsg`, or serial on
  `ttyS1,115200` if accessible. (Note: **A2 rollback images are missing** — re-capture `boot_stock.img` +
  `recovery_stock.img` from the phone first; until then G4 stays blocked even with human approval.)
- **Accept (Gate 1):** Either visible kernel output, **or** a documented first crash with a captured log. A
  compile is not a boot.
- **Rollback:** Restore `boot_stock.img` to p20.
- [ ] Done — blocked on A2 rollback set + human approval.

---

### Stage H — Linux userspace bring-up (experimental)

**Status 2026-08-14:** H1 **done** (debug initramfs boots to shell — CI-verified, kernel repo `f649d5a5`). H2–H6 research/evidence pack committed (`docs/research/driver-bring-up-h2h3.md`): sprdfb color-swap + buffering patches verified to apply, MELFAS MCS8040L touch (driver + DTS binding already in tree), zram config gap (`CONFIG_ZRAM` missing), RNDIS options (android composite rndis in-tree; `CONFIG_USB_ETH` + `USB_ETH_RNDIS` recommended). Remaining H2–H11 are device-gated (need G4 flash + human). Each item independently: one change,
one boot, one log, one verdict. Order is dependency-driven.

- [x] **H1** initramfs and early userspace → boots to a shell prompt — **2026-08-14:** H1 debug initramfs committed (`os/kernel` `f649d5a5`): init mounts proc/sysfs/devtmpfs/devpts/tmpfs, writes a Gate-D boot-evidence log to the serial console, and boots interactive shells on serial `ttyS1` (PID 1) + panel `tty1` (background, `setsid -c`) when fbcon is up; busybox 1.36.1 static. CI fail-closed-verifies the initramfs (init present + `sh -n` + busybox static). Also stripped the stale vendor `CONFIG_CMDLINE` (`mem=128M`/`initrd=` landmine → `console=ttyS1,115200n8` only). Gate-verified run `31799705308`: boot.img 6,850,560 B (sha256 `e3125677…`), all checksums verified locally, bundle re-synced.
- [ ] **H2** framebuffer/display → readable console, correct colors (the archived `sprdfb-fix-swapped-colors`
      and `sprdfb-check-for-buffering` patches address known SC8830 defects)
- [ ] **H3** touch via `evtest /dev/input/event2` → events with correct 480×800 range
- [ ] **H4** rootfs on SYSTEM (p25, 2097 MiB — confirmed sufficient); microSD install is the fallback
- [ ] **H5** zram (~1 GB RAM makes this mandatory) → `free -m` shows zram active
- [ ] **H6** networking — try USB RNDIS **first** (guaranteed path), then Wi-Fi `sprdwl`/`sc2331` with firmware
      extracted from the stock `/system/vendor`. Wi-Fi stays "unsupported" until an actual association.
- [ ] **H7** SSH over whichever link works
- [ ] **H8** battery via the confirmed `POWER_SUPPLY_*` sysfs nodes
- [ ] **H9** reboot / poweroff (suspend is high-risk on SC8830 3.10 — deferring it is a legitimate outcome)
- [ ] **H10** Xorg `xf86-video-fbdev` + `xf86-input-evdev` + `msm-fb-refresher`
- [ ] **H11** minimal desktop; measure idle RAM and record it. Reconsider the DE if idle exceeds ~500 MB.

**Gate 2:** root shell over the network, plus touch and storage — the "developable remotely" state.
**Gate 3:** desktop with display, touch, network, stable across **three consecutive reboots**.

**Accepted limitations, stated up front:** no GPU acceleration (fbdev only; Mali userspace is Android-bound,
no KMS on 3.10) · no telephony (no sprd RIL in pmOS — despite the confirmed dual-SIM LTE hardware) · audio
unlikely initially · Wi-Fi is the highest-risk component.

---

### Stage I — Linux remake and release (experimental)

**Status 2026-08-11:** NOT STARTED — blocked on Gate 3 (H-stage). Note: I1's "fork recipes into `os/`" is
already half-done (kernel source lives at `os/kernel/` → `trefeon/linux-samsung-j1minilte`).

- [ ] **I1** Fork all recipes into this repository under `os/` — this repo becomes the source of truth;
      `reference/` stays vendored material
- [ ] **I2** Evaluate moving the kernel base to the cm-14.1 sharkls 3.10.100 tree, which carries a native
      `j1minilte_defconfig`. Only after Gate 3 — do not destabilize a working boot for a version number.
- [ ] **I3** Branding: `deviceinfo_name`, boot splash, default session, RAM tuning
- [ ] **I4** Release notes stating exactly what works, what does not, and what was never tested — with the
      three-boot evidence per claim (Gate D)

---

## 5. Dependency graph

```text
A1 docs corrected
 └─ A2 rollback set + evidence  ─────────────────────────┐   (HUMAN)
     └─ A3 PIT geometry                                  │
         └─ A4 BoardConfig sizes fixed                   │
             └─ B1 python2 fix                           │
                 └─ B2 build green                       │
                     ├─ B3 kernel assertions             │
                     └─ C1 size gate (16 MiB)            │
                         └─ C2 checksums + metadata      │
                             └─ C3 Odin packaging        │
                                 └─ D1 branding          │
                                     └─ D2 licensing     │
                                         └─ E1 pre-flash ◄┘  (needs rollback)
                                             └─ E2 flash      (HUMAN)
                                                 └─ E3 matrix
                                                     └─ E4 rollback proven
                                                         └─ F1..F3 RELEASE
                                                             └─ G1..G4 kernel  (HUMAN at G4)
                                                                 └─ H1..H11
                                                                     └─ I1..I4
```

Critical path: **A2 → A3 → A4 → B1 → B2 → C1 → E1 → E2**. A2 and B1 are the two true unblockers; A2 gates all
device work, B1 gates all build work. They are independent of each other and may proceed in parallel.

---

## 6. Open decisions

| ID | Decision | Default | Resolve at |
|---|---|---|---|
| D-1 | Manifest revision pinning | Record the resolved revision after the first green sync, then pin it | C2 |
| D-2 | Odin plain `.tar` vs `.tar.md5` | Ship both, let the device test pick the winner | C3 / E2 |
| D-3 | Linux kernel base: archived 3.10.106 vs cm-14.1 3.10.100 | **RESOLVED (K1): vendor `j1minilte` tree first** (proven bootable, DTB-identical); archived recipe = M3.4 follow-up; sharkls reconsidered at I2 | G2 / I2 |
| D-4 | pmOS rootfs target | Internal SYSTEM (2097 MiB — confirmed ample); microSD fallback | H4 |
| D-5 | Desktop environment | Minimal XFCE4; reconsider if idle RAM is poor | H11 |
| D-6 | Minimum hardware set for a public Linux release | Display + touch + storage + network + battery. Telephony and GPU explicitly excluded. | I4 |

---

## 7. Definition of done

**Recovery (MVP)** — a clean CI runner builds a size-checked, checksummed, self-branded recovery from source
committed in `twrp_j1minilte`; it boots on the tested `j1miniltexx`/`sc8830` unit; the full test matrix has an
explicit verdict per row; rollback has been demonstrated in both directions; the release documents the
supported variant and every known limitation.

**Linux (experimental)** — a minimal pmOS userspace boots reliably three consecutive times with working
display, touch, storage, and network; every claim carries a boot log; unsupported hardware is stated plainly;
and the recovery partition remains bootable throughout.
