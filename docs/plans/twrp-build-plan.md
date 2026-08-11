# Custom TWRP Build Plan — SM-J105F (j1minilte)

**Goal:** Build OUR OWN modern TWRP for the J1 mini — replacing the buggy 2017 TWRP 3.0.3-0 (dead MTP, quirky adb, old UI). Custom-branded, built from the 2024 `NotNoelChannel` device tree, which has proven BoardConfig for this exact device (our clone is on its `twrp-5.1` branch — the working branch).

**Status of research:** complete (2026-08-11). Build recipe extracted from the tree's own CI workflow.

---

## 1. Build recipe (ground truth from `twrp_device_samsung_j1minilte/.github/workflows/twrp.yml`)

| Piece | Value |
|---|---|
| Manifest | `minimal-manifest-twrp/platform_manifest_twrp_omni` @ **twrp-6.0** (OMNI/Android 6.0 tree — correct era for a 5.1-shipped device) |
| Device tree | `NotNoelChannel/twrp_device_samsung_j1minilte` @ **twrp-5.1** → `device/samsung/j1minilte` (our local copy == this branch) |
| Kernel | `NotNoelChannel/android_kernel_samsung_j1minilte` @ **recovery** → `kernel/samsung/j1minilte` (3.10.65, `j1minilte_defconfig`, local copy in `reference/kernels/`) |
| Toolchain | **arm-eabi-4.8** (`android-5.1.1_r38` prebuilt from googlesource) at `/opt/toolchains/arm-eabi-4.8/bin` (BoardConfig `KERNEL_TOOLCHAIN` hardcodes this path!) |
| Prebuilt DTB | `device/samsung/j1minilte/prebuilt/dtb` (329 KB, already in tree — `--dt` mkbootimg arg) |
| Build | `export ALLOW_MISSING_DEPENDENCIES=true; source build/envsetup.sh; lunch omni_j1minilte-eng; make -j$(nproc) recoveryimage` |
| Output | `out/target/product/j1minilte/recovery.img` |
| Key BoardConfig items | TW_THEME portrait_hdpi, crypto, MTP on `/dev/mtp_usb`, sprd LUN path, brightness `/sys/class/backlight/panel/brightness`, thermal zone1, ABGR_8888, single buffer, swipe, f2fs cache, `TW_DEVICE_VERSION := 0_notnoelchannel` (OUR branding hook), `TW_HAS_DOWNLOAD_MODE` |

## 2. ⚠️ The one blocker: GitHub Actions no longer has ubuntu-20.04
The tree's workflow pins `ubuntu-20.04`; GitHub retired it **2025-04-15**. Adaptation needed:
- `runs-on: ubuntu-22.04` (or 24.04) — old AOSP 6.0 builds are happiest on 20/22; try 22.04 first
- JDK: workflow sets `~/.jdk_7/java-se-7u75-ri` in PATH but never downloads it (missing/broken step) → use `setup-java` JDK 8 (Zulu) and drop the JDK7 export; omni-6.0 recovery-only builds generally accept JDK8 — if hard errors, fetch JDK7 from a mirror (e.g. AdoptOpenJDK archive)
- arm-eabi-4.8: `git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8 -b android-5.1.1_r38` — if googlesource stalls, mirrors exist (GitHub orgs mirroring `android_prebuilts_gcc_linux-x86_arm_arm-eabi-4.8`)
- Add `setup-swap` (12 GB, as in community TWRP builders) — runners have 7 GB RAM; old make + GCC 4.8 need headroom
- python2 note: minimal-manifest twrp-6.0 branch may need python2 — ubuntu-22.04 has no python2; `actions/setup-python` with 2.7 from... simplest: it's already installed via apt in the 20.04 recipe; on 22.04 add `python2` from `jxu/python2` tap? — handle only if build errors mention python

## 3. Hosting routes (need ONE GitHub account for all)
- **Route A (recommended): fork `NotNoelChannel/twrp_device_samsung_j1minilte` → adapt workflow (fix runner/JDK/swap) → Actions → download `recovery.img` artifact.** Full control, reproducible.
- **Route B: fork `DevCat3/Personl_TWRP_Builder`** (or `Abudfu/Action-Recovery-Builder`): parameterized workflow, TWRP 3.3.1–3.7.1 dropdowns, **Samsung TAR output (Odin-flashable)**, MD5, releases. Set `DEVICE_TREE_URL` = NotNoelChannel tree (or our fork), `twrp-5.1`, device path `device/samsung/j1minilte`, name `j1minilte`, makefile `omni_j1minilte`.
- Route C (fallback, no GitHub): build on a beefy local Linux (acerblue/acergrey if ≥8 GB RAM) with the same recipe — slower to set up, more RAM headroom than vps-01 (892 MB — **too small for AOSP build**, confirmed infeasible).

## 4. "Make it ours" — customization list
1. `TW_DEVICE_VERSION := 0_notnoelchannel` → e.g. `0_j105f-<tag>` — shows in TWRP About
2. `PRODUCT_MODEL` in `omni_j1minilte.mk` → "Samsung Galaxy J1 Mini (custom)"
3. **Splash logo** — TWRP ramdisk boot logo (replaces stock Samsung/blank splash): generate our own 480×800 PNG → build script copies into `bootable/recovery` splash or ramdisk
4. Theme tweaks: TWRP supports custom themes; portrait_hdpi set — optional recolor via `twrp/theme/portrait_hdpi/ui.xml`
5. Defaults: brightness (162), timezone, MTP default on — via TWRP settings-flags in BoardConfig/ramdisk `twrps`
6. **Odin tar** — add workflow step: `tar -c recovery.img > recovery.tar` (patched Odin accepts non-md5 tar) — ready for Odin flashing

## 5. Flash/test flow
1. Artifact `recovery.img` → PC
2. Flash: `adb reboot bootloader`-ish (Samsung download mode) + Odin → AP: `recovery.tar` **or** keep TWRP 3.0.3 installed and: `adb reboot recovery` → in TWRP, `dd if=/sdcard/recovery_new.img of=/dev/block/mmcblk0p21` (RECOVERY partition)
3. Verify: boot into new TWRP → check MTP (should work now — `/dev/mtp_usb` + sprd gadget LUN), adb shell, touch, backup/restore
4. Keep old TWRP backup as rollback (we have stock RECOVERY image + TWRP tar)

## 6. Task checklist
- [ ] User confirms GitHub account (or alternative host)
- [ ] Push/fork device tree (Route A or B)
- [ ] Adapt workflow: ubuntu-22.04, JDK8, swap 12 GB, (python2 if needed)
- [ ] First CI run → recovery.img
- [ ] Customize: TW_DEVICE_VERSION, PRODUCT_MODEL, splash, defaults → rebuild
- [ ] Generate Odin tar artifact
- [ ] Flash on device, verify MTP/adb/touch/backup
- [ ] Save new TWRP as `device/evidence/stock-backup/recovery_custom.img` + commit

## 7. Reference (local)
- Device tree: `reference/device_trees/twrp_device_samsung_j1minilte_notnoel/` (twrp-5.1)
- Recovery kernel: `reference/kernels/android_kernel_samsung_j1minilte_notnoel/` (recovery, 3.10.65)
- Stock RECOVERY partition image (rollback): `device/evidence/stock-backup/recovery_stock.img`
- Community builder workflows: DevCat3/Personl_TWRP_Builder, Abudfu/Action-Recovery-Builder, azwhikaru/Action-TWRP-Builder