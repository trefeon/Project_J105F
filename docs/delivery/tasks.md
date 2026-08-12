# Project J105F Delivery Plan

> Superseded as an execution plan by `docs/delivery/ROADMAP.md`. Retained for reference detail only.

## Goal

Produce a reproducible, genuinely custom recovery and then a bootable Linux/pmOS port for the Samsung SM-J105F. The recovery must build from source committed in this repository; no workflow may clone the device tree or kernel from an external project as its implementation source.

## Current baseline and blockers

- Hardware evidence identifies the tested unit as `j1miniltexx`, `sc8830`, **dual-SIM (DSDS)**, ~1 GB RAM (941,892 kB), firmware `J105FXXS0ARD2`.
- The TWRP source was copied into `twrp/device/samsung/j1minilte` and `twrp/kernel/samsung/j1minilte`.
- The nested TWRP repository is **clean and committed** (`twrp/` → `twrp_j1minilte`, HEAD `2d63e410`); Phase 0 is obsolete (ROADMAP C1). Same for `os/kernel/` → `linux-samsung-j1minilte`.
- GitHub Actions has had repeated failures. The exact failing step must be obtained from the run log before making another speculative workflow change. *(resolved: 6 root causes fixed sequentially, see `docs/build-reports/ci-investigation.md`; both repos green)*
- The Linux target is substantially higher risk: the available VPS was previously determined too small for a full AOSP build, and the kernel/DTB/device bring-up remains incomplete.

## Non-goals

- Do not create a clone script as the product. CI may download the upstream AOSP/TWRP base manifest and toolchain, but the device tree and target kernel implementation must come from this repository.
- Do not flash any image until it passes image inspection and the user explicitly approves the device test.
- Do not commit private device images, keys, modem data, or unreviewed proprietary blobs.
- Do not claim Linux support based only on a successful kernel compile; boot, display, input, storage, USB, and recovery/rollback must be tested separately.

## Phase 0 — Repository hygiene and source ownership

### Task 0.1: Normalize the nested TWRP repository layout

- [x] Confirm the intended repository root contains only project metadata and `device/`, `kernel/` source paths.
- [x] Restore all required device files at `device/samsung/j1minilte/` without losing executable bits, symlinks, binary DTB data, or license files.
- [x] Confirm `kernel/samsung/j1minilte/Makefile` and `j1minilte_defconfig` exist.
- [x] Remove stale root-level duplicates only after checking that no build references them.
- [x] Stage the entire transition in one coherent commit; remove any stale `.git/index.lock` only after confirming no Git process is active.

**Verification (done):** all 15 relocated device files blob-identical to originals (git blob-hash compare); kernel tree 45,061 files incl. Makefile + `j1minilte_defconfig`; `prebuilt/dtb` binary intact; commit `4908f45a`; working tree clean. Windows caveat: `.../nouveau/core/subdev/i2c/aux.c` is an NTFS reserved name — committed blob equals clean-filter (CRLF→LF) output; index entry flagged skip-worktree locally (CI/Linux clones unaffected).

### Task 0.2: Prove the custom-source contract

- [x] Make CI check out this repository and copy only committed local device/kernel paths into the AOSP checkout.
- [x] Add a pre-build assertion that the expected local files exist and that no external device-tree/kernel clone step is present.
- [x] Document the permitted external inputs: upstream TWRP base manifest and compiler only.

**Acceptance (done):** the workflow's copy step reads `$GITHUB_WORKSPACE/device/samsung/j1minilte` and `kernel/samsung/j1minilte` from the checked-out repo; the only network fetches are the manifest sync and the arm-eabi-4.8 prebuilt. No device-tree/kernel clone steps remain. (Delete-network-after-sync equivalence holds because copies happen from the checkout, not the network.)

## Phase 1 — TWRP CI diagnosis and reproducible build

### Task 1.1: Capture the real failure

- [x] Retrieve the complete logs for the latest failed workflow run.
- [x] Classify the first failure as checkout/layout, dependency, Java/Python, manifest sync, compiler, kernel, recovery build, packaging, or artifact upload.
- [x] Record the exact command, error, and runner environment in a build report.

**Verification (done):** `gh run view <run-id> --log-failed` for all three historical runs + first relocated run. Report: `docs/build-reports/ci-investigation.md`. Classifications: action-resolution (31421309135), swap `Text file busy` (31421517523), missing `mkdir` before device-tree copy (31421781959), missing Python 2 (31465251155). All fixed from observed errors; no guessed changes.

### Task 1.2: Make the build environment explicit

- [x] Pin the manifest revision or record the resolved revision after sync. *(manifest-pinned.xml captured from the green build, committed with the CI artifacts; D-1 settled at C2)*
- [x] Use a supported JDK and explicitly install every required legacy host dependency.
- [x] Add Python compatibility only if the failure proves it is required; avoid speculative packages. *(python2 added after run 31465251155 proved it)*
- [x] Make swap creation disk-aware and fail clearly when there is insufficient free disk.
- [ ] Cache only safe, reproducible dependencies; never cache output that can hide a failed source install. *(no caching configured yet — acceptable; re-evaluate after clean build)*

**Acceptance:** the workflow reaches the local device-tree validation step on a clean runner. *(met — run 31465251155 passed checkout/copy/toolchain and reached Build TWRP)*

### Task 1.3: Validate kernel integration before full recovery build

- [x] Check the local kernel tree's expected defconfig name against `BoardConfig.mk`. *(j1minilte_defconfig ✓)*
- [x] Verify `KERNEL_TOOLCHAIN` exists and the compiler can produce an ARM test object. *(CI asserts /opt/toolchains/arm-eabi-4.8/bin/arm-eabi-gcc)*
- [x] Run the kernel build with the exact environment used by the recovery build. *(CI runs it — kernel headers_install + build pass in run 31469647748)*
- [x] Preserve the kernel log as an artifact on failure. *(step log captured; headers_install failure diagnosed from it)*

**Acceptance (met):** kernel image and DTB inputs are produced; earlier failure (missing case-variant headers) named the precise source-tree defect and was fixed at the source.

### Task 1.4: Build and package recovery

- [x] Run `lunch omni_j1minilte-eng` and `make recoveryimage`. *(CI, run 31469647748 — SUCCESS)*
- [x] Confirm output device/product names and recovery partition size. *(out/target/product/j1minilte/recovery.img; 11.34 MiB — fits the real 16 MiB partition per `/proc/partitions`; BoardConfig's 20971520 claim corrected by ROADMAP C4)*
- [x] Inspect the resulting image format, boot header, kernel, ramdisk, DTB, and size. *(ANDROID! header, page 2048, ARM zImage 5.1 MB, gzip ramdisk 6.4 MB, SPRD dt.img with 5 DTBs — all byte-identical to device stock DTBs, SP8835EB board; 11.34 MiB total)*
- [x] Produce `recovery.img` and an Odin-compatible `recovery.tar` as separate artifacts.
- [x] Include SHA-256 checksums and a build metadata file containing source commit, manifest revision, toolchain, and date. *(SHA256SUMS + BUILD_INFO.txt + manifest-pinned.xml published with TWRP and kernel artifacts; re-verified locally, ROADMAP C2)*

**Acceptance:** clean CI produces artifacts reproducibly and fails closed if the image exceeds the recovery partition. *(size-check step active; gate tightened to the real 16,777,216 B per ROADMAP C4/A4/C1 — twrp repo 0f7f3586, green run 31524994619)*

### Checkpoint 1

- [x] TWRP source layout is clean and committed.
- [x] CI failure has a root cause, not a guessed fix.
- [x] A clean runner builds and packages a size-checked recovery image.

**Evidence:** commits 4908f45a (relocation) / dfccd4fb (case-variant headers) / 33819a71 (FR-3 hardening); green run 31472573689; artifact inspected — 5 DTBs byte-identical to stock device DTBs (SP8835EB); 11.34 MiB fits the real 16 MiB partition (ROADMAP C4); SHA256SUMS + BUILD_INFO.txt + manifest-pinned.xml published.

## Phase 2 — Custom recovery quality

### Task 2.1: Identity and licensing

- [x] Replace inherited branding with the project/device identity. *(commit 2d63e410)*
- [x] Set `TW_DEVICE_VERSION` and `PRODUCT_MODEL` consistently. *(0_j105f-custom; "Samsung Galaxy J1 Mini (custom TWRP)")*
- [x] Preserve and audit upstream license notices. *(COPYING AGPL-3.0 preserved; README credits NotNoelChannel)*
- [x] Add a build-info screen or file identifying the source commit. *(BUILD_INFO.txt artifact ✓; `0_j105f-custom` + custom PRODUCT_MODEL verified inside the final image ramdisk, commit 2d63e410)*

### Task 2.2: Recovery functionality

- [ ] Validate boot, touchscreen, display orientation, brightness, reboot/download mode, and key mapping.
- [ ] Validate ADB shell and MTP independently.
- [ ] Validate mounting `/system`, `/data`, `/cache`, internal storage, and external SD where present.
- [ ] Validate backup and restore, including an intentional insufficient-space/error case.
- [ ] Validate encryption behavior; document unsupported encryption instead of silently presenting it as working.

### Task 2.3: Safe device test and rollback

- [ ] Preserve and checksum the stock recovery image and current working TWRP image.
- [ ] Document the exact Odin/AP or `dd` procedure and partition identification.
- [ ] Perform a non-destructive boot/test first where possible.
- [ ] Flash only after explicit user approval.
- [ ] Record test results, photos/logs if available, and rollback outcome.

**Acceptance:** the custom recovery passes the functionality matrix and rollback remains available.

## Phase 3 — Linux/pmOS kernel foundation

**Plan:** `docs/plans/linux-kernel-foundation-plan.md` (detailed execution plan + decisions D5/K1/K2).

### Task 3.1: Choose a build host

- [x] Decide build host strategy (D5). *(CI-first on GitHub Actions ubuntu-22.04, same as TWRP; WSL2 deferred to rootfs phase — not installed today)*
- [x] Use a machine with enough RAM, swap, CPU, and disk for the selected kernel/rootfs workflow. *(CI runners used for kernel; VPS reserved for small cross-compile only)*
- [x] Keep the low-memory VPS for small cross-compilation tasks only unless resource limits are increased.
- [x] Record host toolchain versions and reproducible setup steps. *(arm-eabi-4.8 @ android-5.1.1_r38, ubuntu-22.04, recorded in BUILD_INFO.txt artifact)*

### Task 3.2: Establish the kernel baseline

- [x] Fork kernel source into nested repo `os/kernel/` (FR-1; remote `trefeon/linux-samsung-j1minilte`, commit 90cfeaa5, 45,061 files blob-parity verified vs twrp repo, Windows-hardened).
- [x] Decide kernel base (K1). *(vendor `j1minilte` tree + `j1minilte_linux_defconfig` — proven source; archived IKGapirov recipe deferred to M3.4)*
- [x] Freeze the selected 3.10 source revision and patch set. *(vendor tree @ twrp 4908f45a state; no patches needed for the arm-eabi-4.8 milestone)*
- [x] Apply only patches required for SC8830/J1 Mini bring-up, each with a commit and rationale. *(config delta only: DEVTMPFS/VT/fbcon in j1minilte_linux_defconfig — one commit with rationale)*
- [x] Build the baseline defconfig and save `.config`, compiler version, and image checksum. *(CI saves .config + SHA256SUMS + BUILD_INFO.txt; all verified locally)*
- [x] Confirm whether the target needs a separately supplied DTB or appended DTB. *(SPRD dt.img, 5 DTBs, appended after ramdisk — same as stock; packed from device stock dtbs, byte-identical)*

### Task 3.3: Device-tree and boot arguments

- [x] Derive the DTB from verified stock/recovery evidence and compare nodes against the kernel drivers. *(CI fail-closed gate: dt.img DTBs byte-identical vs tests/stock-dtb = device stock dtbs; kernel-dtc dtbs compared diagnostically — 0/5 identical, expected dtc-version diff, non-gating)*
- [x] Define boot arguments for console, framebuffer, storage, initramfs, and root filesystem. *(base 0x0 / kernel 0x8000 / ramdisk 0x1000000 / second 0xf00000 / tags 0x100 / pgsz 2048; cmdline console=ttyS1,115200n8; busybox debug initramfs)*
- [x] Validate kernel image size and boot header offsets against the Samsung boot layout. *(CI fail-closed verify: header fields + size 6.53 MiB fits the real 16 MiB partition + dt.img byte-identical — VERIFY PASS)*
- [x] Produce a flashable `boot.img` (mkbootimg, SEANDROIDENFORCE appended) + evidence pack (checksums, BUILD_INFO). *(artifacts in device/evidence/build-artifacts/kernel-m31/, checksums verified)*
- [ ] Flash via TWRP Install Image → KERNEL (**after user approval**), record 3 boot attempts + `last_kmsg` where possible, demonstrate rollback from stock boot backup. *(M3.3 — needs user + phone)*

**Acceptance / Gate D (partial):** the device reaches a kernel-visible console or a documented first crash with a captured log; FR-6 evidence report published (`docs/build-reports/kernel-foundation-*.md`). *(M3.1/M3.2 evidence in docs/build-reports/kernel-m31.md; Gate D pending device boot)*

## Phase 4 — Linux userspace and hardware bring-up

Implement in this order, with a boot log and regression note for each item:

1. [ ] initramfs and early userspace
2. [ ] framebuffer/display
3. [ ] touchscreen/input
4. [ ] eMMC/partitions and read-only rootfs
5. [ ] USB gadget/ADB or serial debug
6. [ ] Wi-Fi/Bluetooth, if supported by available firmware
7. [ ] cellular/modem, only after regulatory and proprietary-firmware constraints are understood
8. [ ] battery/charging/thermal sensors
9. [ ] audio/camera/sensors
10. [ ] suspend/reboot/poweroff

**Acceptance:** a minimal pmOS shell boots reliably three times, storage is readable, display/input work, and recovery remains bootable.

## Phase 5 — Release readiness

- [ ] Add documentation for supported variant, known limitations, flash/rollback, and checksums.
- [ ] Ensure CI artifacts are retained and named by commit/version.
- [ ] Run a clean rebuild from a fresh runner.
- [ ] Review repository for secrets/private images/proprietary files.
- [ ] Tag a recovery release only after the device test matrix is complete.
- [ ] Keep Linux port status separate from TWRP release status.

## Dependency graph

```text
source layout cleanup
        ↓
CI failure root cause → explicit environment → kernel integration → recovery image
                                                        ↓
                                      device recovery test + rollback

hardware evidence → kernel baseline → DTB/boot args → early userspace
                                                    ↓
                                      hardware bring-up → pmOS milestone
```

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Legacy TWRP/AOSP host incompatibility | High | Pin revisions, capture first failure, use clean runners, avoid guessed dependency changes |
| Device tree copied incompletely | Critical | Preserve paths, modes, symlinks, binary checksums; validate before build |
| Wrong J105F hardware variant | Critical | Gate every flash/boot test on `j1miniltexx`/`sc8830` evidence |
| Recovery image too large | High | Enforce partition-size check in CI before packaging |
| Flash failure or bad image | Critical | Stock recovery backup, checksum, explicit approval, documented rollback |
| Linux build host too small | High | Move full builds to a larger host; reserve VPS for cross-compile/debug |
| Missing proprietary firmware | Medium/High | Track each firmware dependency and label unsupported hardware honestly |

## Immediate next actions

1. Obtain the first failing CI step from the latest run log.
2. Repair and commit the nested TWRP source relocation before changing build logic again.
3. Make CI validate local `device/` and `kernel/` contents, then rerun once.
4. Only after a clean build, begin the device functionality matrix.
