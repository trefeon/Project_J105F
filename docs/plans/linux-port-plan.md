# Linux Port Plan — SM-J105F (samsung-j1minilte) — postmarketOS (Alpine Linux)

> Superseded as an execution plan by `docs/delivery/ROADMAP.md`. Retained for reference detail only.

**Goal:** Boot a real Linux distribution (postmarketOS / Alpine Linux) on the Samsung Galaxy J1 Mini SM-J105F, by **porting the archived pmOS `samsung-j1mini3g` port** (same SC8830 SoC, sibling model) and then **remaking it** into our own fork.

**Strategy:** Fastest path to a booting baseline = replicate the archived port exactly (proven combo), then iterate device-specific bits (j1minilte), then fork/rebrand/optimize ("remake").

---

## 0. Ground truth already established (from local reference/, 2026-08-11)

| Item | Fact | Source |
|---|---|---|
| Board name | `Spreadtrum_SP8835EB_board` (SC8830 EVB) — 6 DTBs in boot image | `reference/dumps/samsung_j1minilte_dump/bootimg/` |
| Partitions | `KERNEL`→/boot, `SYSTEM`, `userdata`, `CACHE`, `efs`, `HIDDEN`→/preload, `prodnv`, `RECOVERY` — base `/dev/block/platform/sdio_emmc/by-name/`; boot+recovery = **16 MiB** (16,777,216 B per /proc/partitions p20/p21 = 16,384 KiB; BoardConfig's 20971520 overstates - ROADMAP C4), pagesize 2048, kernel cmdline `console=ttyS1,115200n8` | `reference/device_trees/twrp_device_samsung_j1minilte_notnoel/` (BoardConfig.mk, twrp.fstab) |
| Kernel candidates | ① `android_kernel_samsung_j1mini3g` @ `6a377f7` (IKGapirov — source of the pmOS recipe, 3.10.106) ② cm-14.1 sharkls 3.10.100 w/ built-in `j1minilte_defconfig` ③ stock J105F 3.10.x (MayuriLabs) w/ `j1minilte_defconfig` | `reference/docs/pmaports/device/archived/linux-samsung-j1mini3g/APKBUILD`, local kernels |
| WiFi | `drivers/net/wireless/sprdwl` + `sc2331` present in cm-14.1 kernel | `reference/kernels/kernel_samsung_sharkls_gj105f/drivers/net/wireless/` |
| GPU | Mali-400 `r4p0` kernel driver present (Android-lib userspace HAL → **no accel in Linux; fbdev only**) | kernel `drivers/gpu/mali400/` |
| pmOS sibling port | **ARCHIVED** `device/archived/device-samsung-j1mini3g` (pkgver 4) + `device/archived/linux-samsung-j1mini3g` (3.10.106-r8): flash_method=`heimdall-bootimg`, `bootimg_qcdt` (dtbTool-sprd → dt.img), `append_seandroidenforce`, offsets (base 0x0 / kernel 0x8000 / ramdisk 0x1000000 / second 0xf00000 / tags 0x100, pgsz 2048, sparse samsung), touch `/dev/input/event2`, depends incl. `msm-fb-refresher`; kernel patches: gcc7/8/10 compat, `sprdfb-fix-swapped-colors`, `sprdfb-check-for-buffering`, 3.4 piggy.gzip/section; config base = `lineage_j1mini3g_defconfig` | `reference/docs/pmaports/device/archived/` |
| Build recipe | `downstreamkernel_prepare` / `downstreamkernel_package` pmOS helpers; `make ARCH=arm CC=gcc` + `dtbTool-sprd -s 2048` → dt.img; makedepends: `dtbtool-sprd devicepkg-dev mkbootimg msm-fb-refresher` | same APKBUILDs |
| Firmware/blobs | Stock dump has full `/system` (incl. vendor HAL+possible wifi firmware); separate `android_vendor_sprd_gj105f` HALS | `reference/dumps/samsung_j1minilte_dump/system`, `reference/vendor/` |
| Build machine | Windows host → **WSL2 Ubuntu** for pmbootstrap builds; **heimdall on Windows** for flashing | env |
| **User's hardware** | **SM-J105F/DS (Indonesia, XID, dual-SIM) — CONFIRMED via live ADB/TWRP (2026-08-11):** 1 GB RAM (941 892 kB MemTotal), modem `SC9830i` (LTE-capable), board **SP8835EB** (5 DTBs extracted from its stock boot image — same board family as the 3G dump), firmware `J105FXXS0ARD2` (identical build to our cloned dump), kernel `3.10.65-9723235` (2018-04 build), CSC XID. Evidence: `device/evidence/` | live device |

---

## 1. Phased task list (each phase has a gate — no proceeding until gate passes)

### Phase 0 — Safety net + toolchain
| # | Task | Details | Verify |
|---|---|---|---|
| 0.1 | Download stock firmware `J105FXXS0ARD2` (or newer) + Odin 3.13.1 | Links in `docs/research/J105F-CustomOS-Research.md` §5 (samfw.com/firmware/SM-J105F, XDA 3762572) | files present |
| 0.2 | Flash TWRP 3.0.3-0 (SM-J105) via Odin; **full backup → microSD**: EFS, BOOT, SYSTEM, DATA, CACHE | XDA 3545821; TWRP keeps `RECOVERY IS NOT SEAndroid...` warning — harmless | backup zips verified on PC |
| 0.3 | Set up WSL2 Ubuntu 24.04; install `pmbootstrap` (pip); `pmbootstrap init` (own pmaports fork dir, arch=armv7, vendor=samsung) | pmbootstrap docs; keep default stable branch for first build | `pmbootstrap --version` ok |
| 0.4 | Install **heimdall** on Windows; phone into Download Mode; `heimdall print-pit` → **PIT ground truth** (SYSTEM/userdata sizes!) | heimdall-frontend.net Windows build | PIT saved to repo `docs/` |
| 0.5 | ~~Capture the user's stock BOOT image → extract DTBs~~ **DONE (2026-08-11):** boot/efs/recovery/modem raw images `dd`'d from TWRP → `device/evidence/stock-backup/`; **5 DTBs (`SP8835EB board`) extracted** → `.../stock-backup/dtb/` (SPRD dt.img format, 5 entries); these go into our kernel's `dt.img` | done via TWRP adb root shell | DTBs verified (FDT magic, sizes, board strings) |

**Gate 0:** TWRP backup verified restorable + PIT captured + firmware/Odin in hand. **Brick risk is now ~0 (Odin + EFS backup).**

### Phase 1 — Kernel bring-up (the actual "port")
| # | Task | Details | Verify |
|---|---|---|---|
| 1.1 | Recreate `linux-samsung-j1mini3g` recipe as ours: copy archived APKBUILD+config+patches from `reference/docs/pmaports/device/archived/linux-samsung-j1mini3g/` into our pmaports fork as `linux-samsung-j1minilte`; swap source to IKGapirov commit `6a377f7`; pkgname/flavor rename | Keep ALL 8 patches (gcc10 fix is mandatory) + `config-samsung-j1mini3g.armv7` as base | `abuild build` completes |
| 1.2 | Build in WSL2: `pmbootstrap build linux-samsung-j1minilte` → zImage + `dt.img` (dtbTool-sprd, qcdt) | kernel 3.10 + modern GCC — patches handle it | .apk + boot.img artifacts |
| 1.3 | Recreate `device-samsung-j1mini3g` recipe as `device-samsung-j1minilte`: copy deviceinfo + kernel-cmdline.conf; set codename `samsung-j1minilte`, keep `heimdall-bootimg`, qcdt, seandroidenforce, offsets; touch `/dev/input/event2` | offsets/pagesize identical to retained TWRP tree values | `pmbootstrap install` generates boot.img with SEANDROIDENFORCE |
| 1.4 | Flash kernel: `pmbootstrap flasher flash_kernel` (heimdall → KERNEL partition) **or** TWRP → Install Image → KERNEL | Use TWRP first (interactive, verified working) | Reboot → **display shows initramfs/fbcon output OR bootlog** |

**Gate 1:** a kernel boots with visible output (fbcon on display; serial `ttyS1,115200` as fallback if soldering/UART accessible). Debug via cmdline `console=ttyS1` + last_kmsg.

### Phase 2 — Rootfs bring-up (shell first, no UI)
| # | Task | Details | Verify |
|---|---|---|---|
| 2.1 | `pmbootstrap install` (minimal: base + openssh + evtest, **no UI**) → rootfs to SYSTEM partition (heimdall flash SYSTEM, TWRP fallback) | If SYSTEM too small per PIT (0.4) → **Switch decision D2 to `--sdcard` install** (microSD rootfs; SD ≥16 GB) | boots to Alpine login on fbcon |
| 2.2 | Validate inputs: touch via `evtest /dev/input/event2`; display refresh check (msm-fb-refresher already in depends) | deviceinfo touch path already set | events + no garbled fb |
| 2.3 | Storage: mount userdata (internal) or SD as `/home`/media; swap/zram.conf decision (~1 GB RAM → **zram strongly recommended**) | pmOS has zram-init | `free -m` shows zram |
| 2.4 | Network bring-up (pick best first that works): ① **WiFi** — enable `sprdwl`/`sc2331` in config → module + firmware from stock `/system/vendor` (extract from dump) → `/lib/firmware` ② **USB RNDIS** — enable Android RNDIS gadget in kernel config ③ USB tether from second phone | firmware blobs: search dump `system/vendor` for wcn/sc2331 files | `ip a` shows wlan0/usb0; `ssh` from PC |

**Gate 2:** root shell over ssh (wifi or usb) + touch + storage. This is the "developable" state — everything after is done remotely.

### Phase 3 — Graphical UI (usable Linux)
| # | Task | Details | Verify |
|---|---|---|---|
| 3.1 | Xorg with `xf86-video-fbdev` (fbdev, no KMS on 3.10) + `xf86-input-evdev`; `msm-fb-refresher` keeps fb updated | sprd fb quirks already patched (colors/buffering) | `startx` → X root window on display |
| 3.2 | Lightweight DE first pass: **XFCE4 minimal** (xorg-xfce4 default pmOS package set) — measure RAM; fallback sxmo/awesome if >500 MB idle | ~1 GB total — keep DE choices open (decision D3) | desktop + mouse-touch works; `free -m` < 500 MB used idle |
| 3.3 | WiFi GUI (networkmanager) + power basics: battery via sysfs (pmOS has battery monitoring), volume keys, disable suspend (risky on sprd 3.10) | keep scope tight | wifi connect from GUI |

**Gate 3:** full desktop: display + touch + wifi + ssh, stable across reboots.

### Phase 4 — Remake (our fork — the "custom OS" identity)
| # | Task | Details | Verify |
|---|---|---|---|
| 4.1 | **Fork everything into this repo** (`Project_J105F`): kernel config fork, device package fork, our own `deviceinfo` branding (`deviceinfo_name="J1 Mini Linux"` etc.), own config repo layout under `os/` | this git repo becomes the source of truth; reference/ stays as vendored material | `pmbootstrap` rebuilds from OUR tree |
| 4.2 | Kernel refresh: move base to cm-14.1 sharkls 3.10.100 (`kernel_samsung_sharkls_gj105f` — has `j1minilte_defconfig`); merge pmOS config+patches; diff `j1minilte_defconfig` vs pmOS config to enable device-specific bits (wlan, mali, panel) | 3.10.100 > 3.10.106? (sprd fork lineage — verify at build time) | kernel boots, wifi works |
| 4.3 | Userland customizations: custom boot splash (`plymouth` fbdev or boot logo), default session launcher, RAM tuning (zram, minimal services via openrc), optional: overclock CPU via devfreq (spreadtrum cpufreq driver), custom scripts | tkgs in pmOS wiki for each | measurable RAM/boot time gains |
| 4.4 | (Nice-to-have) Upstream back offer: unarchive → pmOS device/community MR for `samsung-j1minilte` | standards: pmOS deviceporting guide | MR reviewable |

**Gate 4:** device boots a custom-branded Lin x experience built 100% from our forked source in this repo.

---

## 2. Decisions (with default)
| ID | Decision | Default | Revisit when |
|---|---|---|---|
| D1 | Kernel base: archived-recipe kernel vs cm-14.1 3.10.100 | **Archived recipe (IKGapirov 3.10.106) for Phases 1–3** (known-good combo) → cm-14.1 swap in Phase 4.2; **if LTE/SC9830A boot issue → use `j3xlte/j3xnlte_defconfig` (SC9830) as config base instead of the j1mini3g one** | Phase 1 gate passes/fails |
| D2 | Install target: internal SYSTEM vs microSD rootfs (`--sdcard`) | **Internal SYSTEM — RESOLVED:** live partition sizes confirm SYSTEM = 2148 MB (mmcblk0p25), userdata 4935 MB, cache 197 MB → rootfs + XFCE fits in SYSTEM; keep SD-install as fallback | PIT/live check done |
| D3 | UI: XFCE4 minimal vs Sxmo | **XFCE4 minimal** (fastest to working desktop); Sxmo as Phase 4 polish | Phase 3.2 RAM measurement |
| D4 | Flash tool: heimdall vs TWRP | **TWRP first** (already flashed, interactive); heimdall as pmOS-native path | whichever fails |
| D5 | Build host: WSL2 vs native Linux | **WSL2** (already on Windows); heimdall runs on Windows side (USB passthrough hassle avoided) | pmbootstrap issues in WSL2 → dual-boot/VM fallback |

## 3. Known limitations (accept up front)
- ❌ GPU acceleration (fbdev-only, X software rendering) — Mali userspace is Android-bound; no KMS/panfrost on 3.10
- ❌ Modem/calls/SMS — no RIL in pmOS for sprd; phone is a pocket Linux computer, not a phone
- ❌ Audio initially (Android HAL audio pipeline; possible later via ALSA if codec exposed — low priority)
- ⚠️ WiFi = highest-risk hardware (sprdwl + firmware blobs) — USB RNDIS/tether is the guaranteed fallback
- ⚠️ ~1 GB RAM — zram + minimal DE mandatory
- ⚠️ Archived port = unmaintained upstream; expect apk/pmbootstrap API drift — pin `pmbootstrap` version for first boot, upgrade later

## 4. Reference material (all local, in `reference/`)
- pmOS recipes (the actual thing being ported): `reference/docs/pmaports/device/archived/{device,linux}-samsung-j1mini3g/`
- j1minilte TWRP tree w/ partition truth: `reference/device_trees/twrp_device_samsung_j1minilte_notnoel/`
- Stock boot img + fstab.sc8830 + init.j1minilte.rc: `reference/dumps/samsung_j1minilte_dump/boot/`
- Kernel candidates: `reference/kernels/{kernel_samsung_sharkls_gj105f, android_kernel_samsung_j1minilte_mayuri, android_kernel_samsung_j1mini3g_*}`
- SoC docs: `reference/docs/scx35l_doc/` · Vendor HAL/firmware: `reference/vendor/`
- Research & sources: `docs/research/J105F-CustomOS-Research.md`

## 5. First actions (next session)
1. 0.1–0.4 (downloads + TWRP backup + PIT) — needs you at the computer with the phone
2. Me (in WSL2 if available): 1.1 recipe fork + kernel build
3. Report back which gate blocks — iterate

---

## 6. Plan update 2026-08-11 (post-Phase-1 evidence)

Executable detail now lives in `docs/plans/linux-kernel-foundation-plan.md` (tasks.md Phase 3). Revisions driven by new evidence:

- **D5 revised — build host:** WSL2 is NOT installed on the Windows host. Kernel build moves CI-first (GitHub Actions ubuntu-22.04, same pattern as the proven TWRP CI); WSL2 install is deferred to the pmbootstrap/rootfs phase where it is actually required.
- **Kernel-base strategy revised (D1 context):** the vendor `j1minilte` kernel tree (already committed at `twrp/kernel/samsung/j1minilte`, built in TWRP CI with `j1minilte_defconfig`) produced a recovery image whose 5 DTBs are byte-identical to the device's stock SP8835EB DTBs. First Linux boot milestone therefore uses **this proven kernel** (change-one-thing-at-a-time: only the initramfs differs from recovery) instead of the archived IKGapirov recipe; the archived recipe becomes the follow-up pmOS-integration milestone after Gate D evidence exists.
- **K2 (new):** milestone-1 initramfs = minimal busybox debug init; `postmarketos-mkinitfs` at rootfs phase.
- Device/partition facts (D2) unchanged and confirmed live: SYSTEM 2148 MB, userdata 4935 MB, cache 197 MB, boot+recovery 16 MiB (ROADMAP C4).