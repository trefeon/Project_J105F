# Linux Kernel Foundation Plan — Phase 3 (SM-J105F)

**Status:** proposed (2026-08-11) · **Gate target:** partial Gate D (PRD) — a bootable kernel reaches a reproducible debug point with 3 recorded boot attempts (FR-6 evidence per milestone).

Maps to: `docs/delivery/tasks.md` Phase 3 (Tasks 3.1–3.3) and `docs/plans/linux-port-plan.md` Phase 1 (kernel bring-up). This document is the executable detail for those; the port plan remains the strategic overview.

---

## 0. Verified input facts (all locally confirmed)

| Item | Fact | Source |
|---|---|---|
| Kernel source (proven bootable) | `kernel/samsung/j1minilte` committed in twrp repo @ 4908f45a — **this exact tree + arm-eabi-4.8 built the recovery whose 5 DTBs are byte-identical to the device's stock DTBs (SP8835EB)** | `docs/build-reports/ci-investigation.md`, run 31469647748 |
| Same vendor source (pristine) | `reference/kernels/twrp_android_kernel_samsung_j1minilte` (matches twrp committed tree), plus 7 sibling/variant clones incl. `android_kernel_samsung_j1mini3g_*` (2017/2018) and `kernel_samsung_sharkls_gj105f` (2022) | `reference/kernels/` |
| pmOS sibling recipe (archived) | `linux-samsung-j1mini3g` pkgver 3.10.106-r8: source = IKGapirov `android_kernel_samsung_j1mini3g` @ `6a377f7c43a84b578df39300dcce9fb9cb387a21` (sha512 pinned), config base `lineage_j1mini3g_defconfig`, 7 patches (gcc7 ilog2, gcc8 put_user, gcc10 extern_YYLOC, ARM-8933 section flag, piggy.gzip.S, sprdfb-swapped-colors, sprdfb-buffering), build = `make ARCH=arm CC=gcc` + `dtbTool-sprd -s 2048 -p scripts/dtc/ -o arch/arm/boot/dt.img arch/arm/boot/dts/` | `reference/docs/pmaports/device/archived/linux-samsung-j1mini3g/APKBUILD` |
| pmOS device pkg (archived) | `device-samsung-j1mini3g`: flash_method `heimdall-bootimg`, generate_bootimg, `bootimg_qcdt=true`, append `SEANDROIDENFORCE=true`, offsets base `0x0` kernel `0x8000` ramdisk `0x1000000` second `0xf00000` tags `0x100`, pagesize 2048, sparse (samsung fmt 1), touch `/dev/input/event2`, 480×800, ext storage | `reference/docs/pmaports/device/archived/device-samsung-j1mini3g/deviceinfo` |
| Boot layout (device-verified) | `ANDROID!` header, page 2048, kernel @ 0x8000, ramdisk @ 0x1000000, SPRD dt.img table (5×20-byte entries, slots at +0x800 + i·0x10000) appended after ramdisk; KERNEL (boot) partition = recovery = **20 MiB (20971520 B)**; cmdline `console=ttyS1,115200n8` | `tools/parse_bootimg.py` runs on stock+our images; `reference/device_trees/twrp_device_samsung_j1minilte_notnoel/BoardConfig.mk` |
| Rollback assets | Stock boot/efs/recovery/modem raw images + DTBs saved in `device/evidence/stock-backup/` (TWRP `dd` backups, checksummed) | `device/evidence/stock-backup/` |
| Toolchain already proven for this kernel | `arm-eabi-4.8` (AOSP android-5.1.1_r38 prebuilt) on ubuntu-22.04 CI runners | TWRP CI workflow |
| pmOS build deps (available locally) | `dtbtool-sprd`, `mkbootimg-osm0sis`, `sm-sparse-image-tool`, `msm-fb-refresher`, `postmarketos-zram` APKBUILDs in `reference/docs/pmaports/main/` | same |
| Build host | **WSL2 is NOT installed on this Windows host** (verified `wsl --status`). VPS too small for full builds (recorded earlier) | env check 2026-08-11 |

---

## 1. Task 3.1 — Build host (DECISION D5, revised)

**Finding:** the port plan's default build host was WSL2 Ubuntu — not installed. Installing WSL2 needs admin + possibly a reboot, and buys nothing for the kernel itself because the exact kernel needed here **already builds green on GitHub Actions** (TWRP CI, ubuntu-22.04).

**Decision (default — confirm at kickoff): CI-first, split by stage.**
1. Kernel image + boot.img assembly → **GitHub Actions ubuntu-22.04** (reuse the proven TWRP workflow pattern: same runner, same `arm-eabi-4.8`, same artifact+checksum discipline; satisfies FR-2/FR-6 by construction).
2. Local WSL2 Ubuntu → **deferred until the pmbootstrap/rootfs phase** (tasks.md Phase 4), where it is genuinely needed for `pmbootstrap` image/rootfs work. Install only then (10 min, admin).
3. VPS → cross-compile/debug scratch only, never primary.

**Recorded (FR-6):** runner ubuntu-22.04, toolchain arm-eabi-4.8 @ android-5.1.1_r38 (or GCC 12 + archived patches for the pmOS-toolchain milestone — see Task 3.2b); kernel source commit; defconfig; image checksums; boot logs.

---

## 2. Task 3.2 — Kernel baseline

### 3.2a Source fork into this repository (FR-1)

Create nested repo `os/kernel/` in the main repository (mirroring the successful `twrp/` nested-repo pattern) with remote e.g. `trefeon/linux-samsung-j1minilte`:

1. Copy the **committed twrp-repo kernel tree** (4908f45a state = already Windows-hardened: 12 case-variant paths + `aux.c` skip-worktree handled). Reuse the exact Phase 0.1 procedure for the 13 problem files.
2. Vendor commit stays intact + a `NOTICE`/README crediting the vendor source (NotNoelChannel / MayuriLabs lineage per `reference/kernels/`) and the pmOS archived recipe (AGPL/GPL-2.0 notices preserved, matching the TWRP COPYING discipline).
3. Defconfig lives in-tree: `arch/arm/configs/j1minilte_defconfig` (already verified present).

### 3.2b Kernel base decision (DECISION K1 — new)

| Option | What | Pros | Cons |
|---|---|---|---|
| **B (default): vendor `j1minilte` tree + `j1minilte_defconfig`** | The exact kernel that already boots on this device (recovery proof) | Zero config/DTB risk; 5-DTB set already matches device byte-identically; fastest path to Gate D; change-one-thing-at-a-time (only the ramdisk/init changes) | Not the pmOS recipe combo; needs a later GCC-compat pass for modern toolchains |
| A: IKGapirov fork @ 6a377f7 (archived recipe) | The pmOS sibling-proven combo (3.10.106 + 7 patches) | Matches archived `linux-samsung-j1mini3g` exactly; patches already battle-tested | Config based on the **3G sibling** (`lineage_j1mini3g_defconfig`) — not proven against our LTE/SC9830i unit; DTB set may differ; more unknowns at first boot |
| C: cm-14.1 sharkls 3.10.100 (has `j1minilte_defconfig`) | Newer sprd fork lineage | Phase 4.2 candidate per port plan | Unproven on our unit; no DTB match evidence |

**Default: B for the first-boot milestone; A (or C) ONLY as follow-up milestones after Gate-D evidence exists.** This revises port-plan D1 (archived-recipe-first) with the evidence we now hold. Revisit trigger: B boots to a dead end at kernel init.

### 3.2c Patches (each with commit + rationale, tasks.md requirement)

For B + arm-eabi-4.8 (first milestone): **no patches expected** (same compiler that already built it). If any are needed, each lands as its own commit with rationale.
Follow-up milestone (B2, pmOS-toolchain parity): apply the archived 7 patches **only if** they apply to this tree; record which apply cleanly vs need porting (`reference/.../linux-samsung-j1mini3g/*.patch` is the source set).

### 3.2d Build + freeze

CI workflow `os/kernel/.github/workflows/kernel.yml` (mirror TWRP CI structure):
- Steps: checkout → arm-eabi-4.8 download → `make ARCH=arm j1minilte_defconfig` → copy saved `.config` to artifact (FR-6) → `make ARCH=arm -j$(nproc) zImage` (+ modules off for milestone 1) → `dtbTool-sprd -s 2048 -o dt.img arch/arm/boot/dts/` (build dtbTool from `reference/docs/pmaports/main/dtbtool-sprd/APKBUILD` in CI if not prebuilt).
- **DTB verification gate:** parse dt.img and byte-compare the 5 DTBs against `device/evidence/stock-backup/dtb/dtb_00..04.dtb` (same check as recovery CI — fail closed on mismatch).
- Artifacts: `zImage`, `dt.img`, `.config`, `SHA256SUMS`, `BUILD_INFO.txt` (kernel commit, defconfig name, toolchain, built_at, cmdline).

**Milestone M3.1:** kernel builds reproducibly in CI, DTBs byte-match stock, checksums published.

---

## 3. Task 3.3 — Boot image + boot arguments

### 3.3a Assembly

- Initramfs — **DECISION K2 (new):** milestone 1 uses a **minimal busybox debug initramfs** (static busybox, `/init` that mounts devtmpfs, boots a shell on fbcon, and if no input, auto-runs a boot-evidence script that prints dmesg markers to the framebuffer; `msm-fb-refresher` equivalent is not needed at this stage since sprd fb is the console). Rationale: smallest possible change over the proven recovery boot; postmarketOS `postmarketos-mkinitfs` initramfs is the Phase 4 (rootfs) integration point.
- `mkbootimg` (AOSP-style, from `mkbootimg-osm0sis` recipe or vendored `mkbootimg.py`): params from device package — base `0x0`, kernel `0x8000`, ramdisk `0x1000000`, second `0xf00000`, tags `0x100`, pagesize 2048, cmdline `console=ttyS1,115200n8` + fbcon/quiet as needed; `--dt dt.img` (SPRD table appended after ramdisk, as stock/images prove).
- Append `SEANDROIDENFORCE` signature padding (deviceinfo `append_seandroidenforce`) so the Samsung bootloader accepts the image via TWRP/Odin paths.
- **Size gate:** ≤ 20 MiB (KERNEL partition), fail closed.

### 3.3b Verification (before any flash)

1. `tools/parse_bootimg.py` on the new boot.img: header fields must match stock layout (page 2048, offsets), DTB table = 5 SP8835EB DTBs byte-identical to stock.
2. `sha256sum` recorded.
3. If the stock cmdline differs (e.g. `androidboot.*` params the bootloader injects), document diffs — kernel must tolerate them.

**Milestone M3.2:** boot.img passes layout+DTB verification, checksummed, flashable.

---

## 4. Flash + boot test (Gate D evidence; requires user + explicit approval)

Per FR-5 discipline and port-plan D4:

1. **Pre-flight:** re-verify stock-backup checksums (`device/evidence/stock-backup/`); confirm current TWRP boots (already validated in Phase 2).
2. **Flash (user, interactive):** TWRP → Install → Install Image → select `boot.img` → partition **KERNEL** (NOT Boot; on this device the bootloader maps recovery-boot via RECOVERY partition and normal boot via KERNEL — confirm partition name against the device's `by-name` list before flashing).
3. **Boot attempt #1:** hold Power → observe: screen output (fbcon: kernel log / debug shell banner), LED/haptics, ADB? Record video/photo of the screen (evidence).
4. On failure: reboot to TWRP (Power+Home+VolUp), grab `last_kmsg` (`cat /proc/last_kmsg` or `dmesg` from the failed boot if preserved), save to `device/evidence/boot-attempts/attempt-N/`.
5. Repeat up to 3 attempts with any cmdline/config change as separate milestones (Gate D requires 3 logs per claimed milestone).
6. **Rollback (must work, ≤5 min):** TWRP → Install Image → stock boot.img from backup → KERNEL → reboot; recovery unaffected by kernel flashes, so rollback is guaranteed.

**Milestone M3.3 / Gate D (partial):** ≥1 of 3 attempts reaches a kernel-visible console (fbcon) or a documented first crash with captured log + last_kmsg; rollback demonstrated. Then: kernel milestone report published with FR-6 fields (source rev, config, toolchain, checksums, boot log, tested-hardware statement).

---

## 5. Milestone/gate summary

| # | Milestone | Gate | Who |
|---|---|---|---|
| M3.1 | Kernel builds reproducibly in CI; DTBs byte-match stock | CI green + checksums | me/CI |
| M3.2 | boot.img (busybox init) verifies against boot layout | parse checks + size ≤ 20 MiB | me/CI |
| M3.3 | Device boots to kernel console/debug point ≥1/3 attempts; rollback OK | Gate D partial + FR-6 report | user + me |
| M3.4 | (follow-up) pmOS-toolchain pass / recipe parity (A or C) | kernel boots with modern GCC | me/CI + user |
| M3.5 | (follow-up) `postmarketos-mkinitfs` initramfs integration | initramfs boots | Phase 4 lead-in |

---

## 6. Decisions (new + revised)

| ID | Decision | Default | Revisit when |
|---|---|---|---|
| D5 (revised) | Build host | **CI-first (GitHub Actions)**; WSL2 deferred to rootfs phase (not installed today) | pmbootstrap work starts (Phase 4) |
| K1 (new) | Kernel source base | **Vendor `j1minilte` tree (B)** for first boot; IKGapirov recipe (A) or sharkls (C) only after Gate D | M3.1 boot dead-end |
| K2 (new) | Initramfs | **Minimal busybox debug init** for M3.3; `postmarketos-mkinitfs` at Phase 4 | M3.3 evidence captured |
| D1 (inherited) | Config base fallback | `j1minilte_defconfig`; if LTE/SC9830i init issue → `j3xlte/j3xnlte_defconfig` (SC9830) | first boot failure mode |
| D4 (inherited) | Flash tool | **TWRP Install Image → KERNEL** first; heimdall for pmOS-native later | whichever fails |
| D2 (inherited, resolved) | Install target | internal SYSTEM (2148 MB) — rootfs phase, not this phase | — |

---

## 7. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Windows case-variant/`aux.c` in new `os/kernel` copy | build/commit breakage | reuse proven skip-worktree procedure from Phase 0.1 (12 paths + aux.c) |
| Black screen (fbcon not enabled in vendor defconfig) | no visible evidence | milestone 1 config delta: `CONFIG_FRAMEBUFFER_CONSOLE=y` (documented, one line, rationale committed); serial ttyS1 as fallback e.g. if UART pads accessed |
| Kernel tolerates injected `androidboot.*` cmdline poorly | boot failure | compare/drop-in stock cmdline in mkbootimg; verify in M3.2 |
| Sprint: dtbTool-sprd build in CI | CI friction | build from local APKBUILD; fallback: pack verified stock DTBs (byte-identical anyway) via script |
| Flash to wrong partition | device impact | pre-flash check of `by-name` list; recovery untouched; rollback path verified first |
| 20 MiB limit | image reject | hard size gate in CI (FR-3 pattern) |
| GCC-compat patches needed for later milestones | delay | archived patch set already local; document apply/port per patch |

---

## 8. Evidence artifacts (FR-6 per milestone)

`docs/build-reports/kernel-foundation-*.md` per milestone + `device/evidence/kernel/`:
- source commit (kernel repo + main repo), `.config` (saved at build), defconfig name
- toolchain + runner versions
- `SHA256SUMS` (zImage, dt.img, boot.img) + `BUILD_INFO.txt`
- boot attempt logs/photos + `last_kmsg` per attempt
- tested-hardware statement (device identity, firmware, partition layout)

---

## 9. First actions (after decisions confirmed)

1. Me: create `os/kernel/` nested repo (copy committed kernel tree, Windows-hardening, vendor NOTICE), push.
2. Me: bootstrap `kernel.yml` CI (build + DTB verify + artifacts), iterate to green (root-cause-only, TWRP CI discipline).
3. Me: busybox initramfs build script + mkbootimg assembly + verification script (reuse `parse_bootimg.py`).
4. Me: M3.2 verification, produce flashable `boot.img` + evidence pack.
5. User: explicit approval → flash via TWRP → boot attempts evidence → rollback check → Gate D report.