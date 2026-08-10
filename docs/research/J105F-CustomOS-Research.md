# SM-J105F (Galaxy J1 Mini) — Custom OS / Linux Research

**Date:** 2026-08-11
**Status:** Research complete — groundwork for "port an existing project, then remake it"
**Local reference copies:** all GitHub repos cloned into `reference/` (see inventory below)

---

## 1. Device identity (verified, not guessed)

| Property | Value | Source |
|---|---|---|
| Model | SM-J105F (Galaxy J1 Mini, 2016) | `system/build.prop` in dump |
| Codename | `j1minilte` (product `j1miniltexx`) | dump `build.prop` |
| Platform | Spreadtrum/Unisoc **SC8830** (platform name: **sharkls**, family SCX35L) | dump `ro.board.platform=sc8830`, kernel tree `scx35l/sharkls` |
| CPU | 4× ARM Cortex-A7 @ 1.2 GHz (32-bit, ARMv7) | devicespecifications.com |
| GPU | Mali-400 MP2 | devicespecifications.com |
| RAM | 768 MB (some variants 1 GB) | devicespecifications / gsmarena |
| Storage | 8 GB eMMC + microSD (up to 128 GB, shares SIM2 slot) | phonebunch |
| Display | 4.0" TFT 480×800 | devicespecifications |
| Stock OS | Android 5.1.1 Lollipop (API 22), build **J105FXXS0ARD2** | dump build.prop / play-store-api |
| Kernel (stock) | Linux 3.10.65 | LegacyOS/Dmitry kernel trees |
| Battery | 1500 mAh removable | — |
| Boot | Samsung legacy boot — `KERNEL` partition (`/dev/block/platform/sdio_emmc/by-name/KERNEL`, mmcblk0p20 on sibling J3), boot image needs `SEANDROIDENFORCE` suffix | Mardy's halium J3 notes |

> ⚠️ Sibling models matter: **SM-J105H/B** = codename `j1mini3g` (also SC8830, same sharkls platform). Much of the working Linux/ROM work on GitHub is for `j1mini3g` and transfers to `j1minilte` with minor changes. **SM-J106\*** (J1 Mini Prime, `j1minivelte`, SC9830) and **SM-J120\*** (J1 2016, `j1xlte`, Exynos 3475) are DIFFERENT SoCs — ignore them (j1xlte is Exynos, not Spreadtrum).

---

## 2. GitHub resource inventory (all cloned into `reference/`)

### 2.1 Kernels — the most important category

| Repo | Local path | What it is | Why it matters |
|---|---|---|---|
| `Galaxy-J105F-Resources/kernel_samsung_sharkls` (branch **cm-14.1**) | `reference/kernels/kernel_samsung_sharkls_gj105f` | Linux **3.10.100** scx35l/sharkls kernel with **`j1minilte_defconfig`** already present (plus j3xlte/j3xnlte defconfigs) | **THE kernel for a custom ROM.** CyanogenMod 14.1-era tree for our exact device |
| `MayuriLabs/android_kernel_samsung_j1minilte` | `reference/kernels/android_kernel_samsung_j1minilte_mayuri` | Samsung open-source kernel for SM-J105F (3.10.x, stock) | Base kernel = stock J105F source |
| `TeamWin/android_kernel_samsung_j1minilte` (branch `android-5.1`) | `reference/kernels/twrp_android_kernel_samsung_j1minilte` | Kernel used to build TWRP for j1minilte | Recovery kernel base |
| `NotNoelChannel/android_kernel_samsung_j1minilte` (branch `recovery`, 2024) | `reference/kernels/android_kernel_samsung_j1minilte_notnoel` | Fresh (2024) fork of TWRP kernel with `recovery` branch | Modern recovery work |
| `djeman/android_kernel_samsung_sharkls` (branch **lineage-15.1**) | `reference/kernels/android_kernel_samsung_sharkls_djeman` | sharkls platform kernel for **LineageOS 15.1 (Android 8.1)** on Samsung J3 (j3xlte/j3xnlte) | Most advanced sharkls kernel — full Android 8.1 bootable platform |
| `LegacyOS/android_kernel_samsung_j1mini3g` (branch `APB1_CIS`) | `reference/kernels/android_kernel_samsung_j1mini3g_legacyos` | Stock 3.10.65 kernel for SM-J105H/B (`j1mini3g`) | Same SoC as ours — stock source for comparison |
| `Dmitry3381102/android_kernel_samsung_j1mini3g` | `reference/kernels/android_kernel_samsung_j1mini3g_dmitry` | Unofficial 5.1.1 kernel for SM-J105H; builds via `make j1mini3g-dt_defconfig && make -j2` | Simplest known-good standalone kernel build recipe |
| `xchetah/spreadtrum-kernel-common` | `reference/kernels/spreadtrum-kernel-common_xchetah` | Spreadtrum common kernel (SC7731C/G, SC8831 + more) | Cross-SoC reference for drivers |

### 2.2 Device trees

| Repo | Local path | What it is |
|---|---|---|
| `djeman/android_device_samsung_sharkls-common` (branch **lineage-15.1**) | `reference/device_trees/android_device_samsung_sharkls-common_djeman` | **Complete shared device tree for the whole sharkls platform**: BoardConfigCommon, `sharkls.mk`, `treble.mk`, sepolicy, RIL, GPS, IMS, init, keylayout, libshims, recovery, and the famous `patches/` (sprd-diff: framework/AV/base patches needed to build the platform) |
| `djeman/android_device_samsung_j3xnlte` (branches cm-13.0, cm-14.1, lineage-15.1) | `reference/device_trees/android_device_samsung_j3xnlte_djeman` | Reference per-device tree on top of sharkls-common (extract-files.sh, proprietary-files.txt) — **template for writing our j1minilte tree** |
| `NotNoelChannel/twrp_device_samsung_j1minilte` (2024) | `reference/device_trees/twrp_device_samsung_j1minilte_notnoel` | TWRP device tree for j1minilte (with prebuilt kernel) |
| `twrpdtgen/android_device_samsung_j1minivelte` | `reference/device_trees/android_device_samsung_j1minivelte_twrpdtgen` | Auto-generated tree for J106F — partition-layout reference only |
| `Galaxy-J105F-Resources/samsung_j1minilte_dump/twrp-device-tree/` | inside `reference/dumps/samsung_j1minilte_dump` | Auto-generated TWRP tree from the real device dump |

### 2.3 Vendor / HAL (proprietary + open Spreadtrum sources)

| Repo | Local path | What it is |
|---|---|---|
| `Galaxy-J105F-Resources/android_vendor_sprd` | `reference/vendor/android_vendor_sprd_gj105f` | **FULL Spreadtrum vendor tree**: `proprietaries/scx35l` (prebuilt system blobs), open-source HAL sources (camera ISP 1.0/2.0, Mali GPU utgard with **sc8830** platform dir, audio APM normal/whale, WCN wifi/bt/fm incl. **sc2331 wifi driver** 4.4/5.1/6.0) |
| `djeman/android_vendor_samsung_common` (lineage-15.1) | `reference/vendor/android_vendor_samsung_common_djeman` | Samsung common vendor bits used by sharkls LOS 15.1 builds |
| `djeman/android_vendor_sprd` | ⛔ **DEAD — DMCA takedown** (Unisoc, Feb 2026: github.com/github/dmca/blob/master/2026/02/2026-02-03-unisoc-3.md) | The LOS 15.1 vendor tree is gone from GitHub. **Our `android_vendor_sprd_gj105f` copy is one of the surviving snapshots — treat it as precious, keep offline backups.** Forks may exist under other owners |

### 2.4 Docs & misc

| Repo | Local path | What it is |
|---|---|---|
| `Bonstra/scx35l_doc` | `reference/docs/scx35l_doc` | Reverse-engineered documentation of the **SCX35L family (SC8830/SC9830i)** from GPL source + datasheets — the closest thing to a SoC manual we have |
| `luisadha/M3P` | `reference/misc/M3P` | mkshrc mod project for SM-J105F (terminal prompt mods) — proof of active hobbyist interest |
| `ravindu644/Droidspaces-OSS` | `reference/misc/Droidspaces-OSS` | Open-source AI assistant launcher that explicitly added `j1minilte` support in 2026 — i.e., people still actively target this device |

---

## 3. The landscape: what can we actually build?

### Path A — Custom Android ROM (recommended starting point) ✅ realistic
- **No ROM ever shipped for SM-J105F** (XDA confirms: "not even one custom rom"), but the *platform* is proven:
  - **CM 14.1 (Android 7.1)**: `j1minilte_defconfig` exists in the cm-14.1 kernel; 4PDA thread (886192) has CM12/CM13 porting links for the J105 family; users reported PAC-ROM / Resurrection Remix (7.1-based) running on J105B via ports.
  - **LineageOS 15.1 (Android 8.1)**: djeman's full sharkls platform tree (kernel + sharkls-common + vendor) booted Android 8.1 on the J3 (j3xlte/j3xnlte) — same SoC platform, same `fstab.sc8830`, same HALs. **Port = new per-device tree (`device/samsung/j1minilte`), reuse sharkls-common + kernel + vendor.**
  - **TWRP 3.0.3-0** exists for SM-J105 (XDA, Odin-flashable) — quirky but real (known bugs: MTP broken, "not SEAndroid enforcing" warning; workaround exists).
- **Reality check**: 768 MB RAM — Android 7.1 is usable but tight; Android 8.1 is heavy. CM12.1/CM13 (5.1/6.0) would be the *snappiest* custom ROMs; 14.1 is the sweet spot for feature balance.

### Path B — Real Linux: postmarketOS (Alpine Linux on the phone) ✅ most realistic "Linux OS"
- postmarketOS has a **device port for the sibling `samsung-j1mini3g` (SM-J105H/B, same SC8830 SoC)**: kernel package **`linux-samsung-j1mini3g` 3.10.106-r8** (armv7, built 2025-04-02) — a fork of the Samsung 3.10 kernel with pmOS patches.
- `samsung-j1minilte` has a wiki page but **no confirmed device/kernel packages** → for our exact J105F we either (a) verify/port the `j1mini3g` device package (same SoC, minor variant differences), or (b) create a `j1minilte` device package in pmaports using the same kernel recipe.
- Install model: flash pmOS rootfs to the system partition via TWRP/Odin + the 3.10 kernel → a genuine **Linux 3.10 distro** with Alpine. GUI: XFCE4/Sxmo/i3 (Plasma Mobile is too heavy for 768 MB).
- This is the classic "Linux on old phone" route and the most achievable full-Linux goal.

### Path C — Halium / Ubuntu Touch (Lomiri) 🔶 possible, heavy
- Halium 7.1 port was proven on the **same SoC platform** (Samsung J3 `j3xnlte`): boot image + system image built, LXC container boots, libhybris tests mostly pass (camera works in the UT camera app; audio HAL was the pain point — `audio.primary.sc8830.so`).
- Blueprint: halium-7.1 + LOS 14.1 tree for sharkls + our j1minilte device tree + `SEANDROIDENFORCE` boot suffix.
- Ubuntu Touch on 768 MB RAM is rough but there are success stories with Sxmo-class usage. Given RAM, treat as stretch goal.

### Path D — Mainline Linux (modern kernel, e.g. 6.x) ❌ not realistic
- Mainline `sprd` support covers **SC9836/SC9860/SC9863A/UMS512** (arm64, newer Unisoc) — **SC8830 has zero mainline support** (no clk/pinctrl/PMIC/GPU/display drivers for it; even the arm32 sprd mach code was never merged).
- Porting SC8830 to a modern kernel = writing drivers from scratch (months–years of kernel work). **Not recommended** — the Samsung 3.10 fork (used by pmOS) IS the pragmatic "Linux" for this hardware.

### Path E — Linux via chroot on stock Android (easiest, no flashing risk) ✅ zero-risk
- Termux (old builds work on 5.1) / UserLAnd / LinuxDeploy / **Droidspaces** (explicitly supports `j1minilte`, fixed ramfs detection for it in 2026) → Debian/Ubuntu/Arch rootfs + X11 over VNC. No bootloader risk. Good for learning Linux-on-device before committing to Path A/B.

---

## 4. Recommended strategy: "port the existing project, then remake it"

1. **Phase 0 (recovery safety net):** Flash TWRP 3.0.3-0 (SM-J105) via Odin; back up EFS + everything (Samsung stock 5.1.1: J105FXXS0ARD2 available at samfw). Never skip this — Spreadtrum devices brick hard if EFS is lost.
2. **Phase 1 (custom ROM — port djeman's sharkls LOS 14.1/15.1):**
   - Base: LOS 14.1 (matches our cm-14.1 kernel + j1minilte_defconfig) — or 15.1 if we want the newer tree.
   - Write `device/samsung/j1minilte/` modeled on `j3xnlte/` (BoardConfig.mk, lineage.mk, extract-files.sh, proprietary-files.txt).
   - Use `reference/kernels/kernel_samsung_sharkls_gj105f` (cm-14.1, has j1minilte_defconfig) for 14.1, or djeman's lineage-15.1 kernel for 15.1.
   - Vendor: extract blobs from our `samsung_j1minilte_dump/system` (or fresh firmware dump via dumpyara) + `android_vendor_sprd_gj105f` for the open HAL sources. Apply `sharkls-common/patches/apply_sprd-diff.sh` (frameworks patches) — known required for system image to build.
   - Kernel defconfig: `j1minilte_defconfig` → `make ARCH=arm j1minilte_defconfig` with arm-eabi-4.8/4.9 toolchain.
3. **Phase 2 (Linux OS — port pmOS `j1mini3g` to `j1minilte`):**
   - Take the `samsung-j1mini3g` pmaports device + kernel recipes (kernel 3.10.106 fork), clone to `samsung-j1minilte`, adjust for J105F (RAM 768 MB, modem/radio differences, display/panel DTS if any).
   - Boot via TWRP: flash `boot.img` (kernel) + system rootfs; or use Odin for the kernel image with SEANDROIDENFORCE.
4. **Phase 3 (remake):** this is where "remake it" happens — fork the ported tree into our own project, rename branding, customize the UI/framework, add features. This repo (`Project_J105F`) becomes the home of the forked source.

---

## 5. Files you should download manually (I can't fetch these reliably here)

| # | Item | Where | Why |
|---|---|---|---|
| 1 | **TWRP 3.0.3-0 for SM-J105** (Odin tar) | XDA thread 3545821 → androidfilehost fid=529152257862700709 | Recovery — entry point for everything |
| 2 | **Stock firmware SM-J105F** (J105FXXS0ARD2 or newer, your CSC) | samfw.com/firmware/SM-J105F (or sammobile) | Brick-recovery + blob extraction source |
| 3 | **Odin 3.13.1 patched** | XDA thread 3762572 | Flashing tool (Windows) |
| 4 | **arm-eabi-4.8 / arm-eabi-4.9 toolchain** | e.g. android.googlesource.com platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8 (or aosp mirror), or `android_prebuilt_toolchains` mirrors on GitHub | Building the 3.10 kernel |
| 5 | (For full ROM builds) **AOSP/LineageOS source** — do NOT download manually; `repo init` pulls it during setup | — | Build environment (Linux/WSL2 recommended, 100+ GB) |
| 6 | (Optional) **pmbootstrap** | pip install pmbootstrap | postmarketOS builds (Path B) |
| 7 | (Optional) 4PDA J1 mini thread (Russian forum — needs account) | 4pda.to/forum/index.php?showtopic=886192 | CM12/CM13 port links + FRP bypass + service firmware for J105 |
| 8 | (Optional) **SuperSU 2.82** (Android 5.1 root) or Magisk (6.0+ only) | official channels | Root for stock experimentation |

> Note: `djeman/android_vendor_sprd` was DMCA'd off GitHub — **do not rely on re-cloning it**; if you need it again, mirror our local copy to your own GitHub/offline storage.

---

## 6. Key sources

- GitHub orgs/repos: `Galaxy-J105F-Resources` (kernel_samsung_sharkls, samsung_j1minilte_dump, android_vendor_sprd), `MayuriLabs/android_kernel_samsung_j1minilte`, `TeamWin/android_kernel_samsung_j1minilte`, `NotNoelChannel/{android_kernel,twrp_device}_samsung_j1minilte`, `djeman/{android_kernel_samsung_sharkls, android_device_samsung_sharkls-common, android_device_samsung_j3xnlte, android_vendor_samsung_common, android_vendor_sprd}`, `LegacyOS/android_kernel_samsung_j1mini3g`, `Dmitry3381102/android_kernel_samsung_j1mini3g`, `xchetah/spreadtrum-kernel-common`, `Bonstra/scx35l_doc`, `twrpdtgen/android_device_samsung_j1minivelte`, `luisadha/M3P`, `ravindu644/Droidspaces-OSS`
- postmarketOS: wiki pages `Samsung_Galaxy_J1_mini_(samsung-j1minilte)` and `(samsung-j1mini3g)`; package `linux-samsung-j1mini3g` 3.10.106-r8; MR !533 "samsung-j1mini3g: new device"
- Mainline status: lkddb `CONFIG_ARCH_SPRD` (arm64, 4.1+); LWN patchsets for Sharkl/SC9860; tuxphones.com article (Unisoc mainline activity — none for SC8830)
- Halium: `Halium/projectmanagement#261` (j3xnlte halium-7.1 checklist); mardy.it blog "Notes on porting the Samsung J3 to Halium + Ubports" (KERNEL partition mmcblk0p20, SEANDROIDENFORCE, fstab.sc8830)
- XDA: `[RECOVERY] TWRP 3.0.3-0 for Samsung J1 Mini (SM-J105)` (3545821), `[CLOSED] twrp for j1 mini (sm-j105m/ds...)` (4637839), "is there any tried custom Rom for sm-j105h" (3833693)
- Specs: devicespecifications.com (SC8830/768 MB), gsmarena, phonebunch, samfw.com

## 7. Unknowns / open questions

1. Exact pmOS status of `samsung-j1minilte` (wiki page exists; package index unverifiable behind anti-bot). Verify via `pmbootstrap init` when you set up pmOS.
2. Whether the CM 14.1 `j1minilte_defconfig` was ever booted on hardware (kernel exists; ROM evidence on 4PDA/XDA is anecdotal — J105B ran PAC-ROM/RR ports).
3. J105F vs J105H/B hardware deltas (RAM 768 MB vs 1 GB, radio bands, panel driver) — needed for both ROM and pmOS ports; answerable from the stock firmware/dump once on a Linux build box.
4. TWRP 3.0.3-0 quirks (MTP, SEAndroid warning) — modern TWRP could be rebuilt from `NotNoelChannel` trees instead.
5. dmca risk: remaining `android_vendor_sprd` forks may vanish; take local backups.

## 8. What's next (when you're ready)

- [ ] Set up a Linux build machine (WSL2 or bare metal, ≥100 GB free, 16 GB RAM recommended)
- [ ] Install TWRP + take full backup of the phone (EFS!)
- [ ] Phase 1: create `device/samsung/j1minilte` tree (j3xnlte template + dump blobs) and attempt a LOS 14.1 build
- [ ] Phase 2: pmOS port (`samsung-j1minilte` device package from `j1mini3g` recipe)
- [ ] Phase 3: fork + rebrand + customize ("remake")
