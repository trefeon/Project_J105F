# Project J105F Delivery Plan

## Goal

Produce a reproducible, genuinely custom recovery and then a bootable Linux/pmOS port for the Samsung SM-J105F. The recovery must build from source committed in this repository; no workflow may clone the device tree or kernel from an external project as its implementation source.

## Current baseline and blockers

- Hardware evidence identifies the tested unit as `j1miniltexx`, `sc8830`, single-SIM, 1 GB RAM, firmware `J105FXXS0ARD2`.
- The TWRP source was copied into `twrp/device/samsung/j1minilte` and `twrp/kernel/samsung/j1minilte`.
- The nested TWRP repository currently has a broken working-tree transition: source files were deleted from the repository root while replacement copies are untracked under `device/` and `kernel/`. This must be resolved before treating the source layout as committed.
- GitHub Actions has had repeated failures. The exact failing step must be obtained from the run log before making another speculative workflow change.
- The Linux target is substantially higher risk: the available VPS was previously determined too small for a full AOSP build, and the kernel/DTB/device bring-up remains incomplete.

## Non-goals

- Do not create a clone script as the product. CI may download the upstream AOSP/TWRP base manifest and toolchain, but the device tree and target kernel implementation must come from this repository.
- Do not flash any image until it passes image inspection and the user explicitly approves the device test.
- Do not commit private device images, keys, modem data, or unreviewed proprietary blobs.
- Do not claim Linux support based only on a successful kernel compile; boot, display, input, storage, USB, and recovery/rollback must be tested separately.

## Phase 0 — Repository hygiene and source ownership

### Task 0.1: Normalize the nested TWRP repository layout

- [ ] Confirm the intended repository root contains only project metadata and `device/`, `kernel/` source paths.
- [ ] Restore all required device files at `device/samsung/j1minilte/` without losing executable bits, symlinks, binary DTB data, or license files.
- [ ] Confirm `kernel/samsung/j1minilte/Makefile` and `j1minilte_defconfig` exist.
- [ ] Remove stale root-level duplicates only after checking that no build references them.
- [ ] Stage the entire transition in one coherent commit; remove any stale `.git/index.lock` only after confirming no Git process is active.

**Verification:** `git status --short`; `git ls-files device/samsung/j1minilte kernel/samsung/j1minilte`; verify the DTB checksum and file mode; inspect `git diff --cached --stat`.

### Task 0.2: Prove the custom-source contract

- [ ] Make CI check out this repository and copy only committed local device/kernel paths into the AOSP checkout.
- [ ] Add a pre-build assertion that the expected local files exist and that no external device-tree/kernel clone step is present.
- [ ] Document the permitted external inputs: upstream TWRP base manifest and compiler only.

**Acceptance:** deleting network access after the base manifest/toolchain stage still leaves the device tree and kernel available from the checked-out repository.

## Phase 1 — TWRP CI diagnosis and reproducible build

### Task 1.1: Capture the real failure

- [ ] Retrieve the complete logs for the latest failed workflow run.
- [ ] Classify the first failure as checkout/layout, dependency, Java/Python, manifest sync, compiler, kernel, recovery build, packaging, or artifact upload.
- [ ] Record the exact command, error, and runner environment in a build report.

**Verification:** `gh run view <run-id> --log-failed` (or equivalent saved CI log); identify the earliest actionable error, not a downstream cascade.

### Task 1.2: Make the build environment explicit

- [ ] Pin the manifest revision or record the resolved revision after sync.
- [ ] Use a supported JDK and explicitly install every required legacy host dependency.
- [ ] Add Python compatibility only if the failure proves it is required; avoid speculative packages.
- [ ] Make swap creation disk-aware and fail clearly when there is insufficient free disk.
- [ ] Cache only safe, reproducible dependencies; never cache output that can hide a failed source install.

**Acceptance:** the workflow reaches the local device-tree validation step on a clean runner.

### Task 1.3: Validate kernel integration before full recovery build

- [ ] Check the local kernel tree's expected defconfig name against `BoardConfig.mk`.
- [ ] Verify `KERNEL_TOOLCHAIN` exists and the compiler can produce an ARM test object.
- [ ] Run the kernel build with the exact environment used by the recovery build.
- [ ] Preserve the kernel log as an artifact on failure.

**Acceptance:** a kernel image and required DTB inputs are produced, or the build report names the precise incompatible source/config/toolchain assumption.

### Task 1.4: Build and package recovery

- [ ] Run `lunch omni_j1minilte-eng` and `make recoveryimage`.
- [ ] Confirm output device/product names and recovery partition size.
- [ ] Inspect the resulting image format, boot header, kernel, ramdisk, DTB, and size.
- [ ] Produce `recovery.img` and an Odin-compatible `recovery.tar` as separate artifacts.
- [ ] Include SHA-256 checksums and a build metadata file containing source commit, manifest revision, toolchain, and date.

**Acceptance:** clean CI produces artifacts reproducibly and fails closed if the image exceeds the 20 MiB recovery partition.

### Checkpoint 1

- [ ] TWRP source layout is clean and committed.
- [ ] CI failure has a root cause, not a guessed fix.
- [ ] A clean runner builds and packages a size-checked recovery image.

## Phase 2 — Custom recovery quality

### Task 2.1: Identity and licensing

- [ ] Replace inherited branding with the project/device identity.
- [ ] Set `TW_DEVICE_VERSION` and `PRODUCT_MODEL` consistently.
- [ ] Preserve and audit upstream license notices.
- [ ] Add a build-info screen or file identifying the source commit.

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

### Task 3.1: Choose a build host

- [ ] Use a machine with enough RAM, swap, CPU, and disk for the selected kernel/rootfs workflow.
- [ ] Keep the low-memory VPS for small cross-compilation tasks only unless resource limits are increased.
- [ ] Record host toolchain versions and reproducible setup steps.

### Task 3.2: Establish the kernel baseline

- [ ] Freeze the selected 3.10.106 source revision and patch set.
- [ ] Apply only patches required for SC8830/J1 Mini bring-up, each with a commit and rationale.
- [ ] Build the baseline defconfig and save `.config`, compiler version, and image checksum.
- [ ] Confirm whether the target needs a separately supplied DTB or appended DTB.

### Task 3.3: Device-tree and boot arguments

- [ ] Derive the DTB from verified stock/recovery evidence and compare nodes against the kernel drivers.
- [ ] Define boot arguments for console, framebuffer, storage, initramfs, and root filesystem.
- [ ] Validate kernel image size and boot header offsets against the Samsung boot layout.

**Acceptance:** the device reaches a kernel-visible console or a documented first crash with a captured log.

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
