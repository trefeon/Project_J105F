# Exact Model Identification — SM-J105F/DS (confirmed)

**Date:** 2026-08-14 · **Method:** local-dump evidence mining + web research (two parallel lanes, independently convergent)

## Verdict

The unit is a **Samsung Galaxy J1 Mini 4G** (marketing alias "Galaxy J1 Nxt") — **SM-J105F/DS** (dual-SIM),
codename `j1minilte` / product `j1miniltexx`, CSC **XID (Indonesia)**.

The SoC is the **LTE Spreadtrum SC9830I** (SharkLS platform, SCX35L family — same silicon line the spec
sites call SC9830A). It is **NOT** the 3G-only SC8830.

### Identity table

| Property | Value | Source (local evidence) |
|---|---|---|
| Model / product | SM-J105F / `j1miniltexx` | `device/evidence/getprop.txt:805,809` |
| Codename | `j1minilte` | `device/evidence/getprop.txt:795` |
| CSC | XID (INDONESIA) | `device/evidence/getprop.txt:617-621` |
| Firmware | J105FXXS0ARD2 (build 5.1.1 / LMY47V) | `device/evidence/getprop.txt:517,555` |
| Kernel (stock) | 3.10.65-9723235 (dpi@SWDG9706) | `device/evidence/version.txt` |
| Chip | **SC9830I** | `getprop.txt:569,781` (`ro.chipname`, `ro.product.board`) |
| Hardware | `SS_SHARKLS` (SC9830I LTE family marker) | `getprop.txt:797` |
| Modem modes | GSM,EDGE,TD-SCDMA,WCDMA,**TD-LTE,FDD-LTE** | `getprop.txt:807` |
| RAM | ~1 GB (941,892 kB) | `device/evidence/meminfo.txt` |
| Board (DTB) | "Spreadtrum SP8835EB board", `sprd,sc-id=<0x2666 …>` (**0x2666 = 9830**) | `reference/dumps/samsung_j1minilte_dump/bootdts/02..06.dts`, kernel DTS rev00 |

## Why "sc8830" is everywhere but does NOT mean the 3G chip

`ro.board.platform=sc8830`, `ro.hardware=sc8830`, cpuinfo `Hardware: sc8830`, dmesg `Machine: sc8830`,
and even the SP8835EB board string are the **platform-family name shared by the entire SCX35 / SCX35L
family** — both 3G (SC8830) and LTE (SC9830i) silicon report it. Proof: the same pairing
(`TARGET_BOARD_PLATFORM := sc8830` + `TARGET_BOOTLOADER_BOARD_NAME := SC9830I`) is used by djeman's
SC9830i J3 tree and by our own TWRP BoardConfig.mk.

## Decisive LTE signals (all present in this unit)

| Signal | Value | Evidence |
|---|---|---|
| `ro.chipname` / `ro.product.board` | `SC9830I` | `getprop.txt:569,781` |
| `ro.product.hardware` | `SS_SHARKLS` | `getprop.txt:797` |
| Modem mode | includes TD-LTE, FDD-LTE | `getprop.txt:807` |
| LTE modem stack | `persist.modem.l.enable=1`, `/proc/cptl/`, `/dev/stty_lte`, `spipe_lte` | `getprop.txt:653-679`, ramdisk rc files |
| Boot DTB | `sprd,sc-id = <0x2666 …>` (**9830**), `clk_ltepll` node | dump bootdts, kernel DTS rev00 |
| Kernel config | `CONFIG_ARCH_SCX35L=y`, `CONFIG_MACH_J1MINILTE=y`, **`CONFIG_MACH_SP9830I=y`**, **`CONFIG_SIPC_LTE=y`**, `# CONFIG_SPRD_MODEM_TD is not set` | all 4 j1minilte defconfigs; `os/kernel` linux config |
| Partition table | LTE modem set `l_modem` (p8), `l_fixnv1/2` (p3/p4), `l_runtimenv1/2` (p12/p13), `l_gdsp` (p9), `l_ldsp` (p7), `l_warm` (p10), `td_runtimenv1/2` (p14/p15); **no plain 3G `modem` partition** | `device/evidence/byname.txt` |
| cmdline | `tlfixnv=…,0x90000 tlruntimenv=…,0xb4000` | `device/evidence/cmdline.txt` |
| RIL | `rild.libpath2=libsec-ril-dsds.so` (dual-SIM DSDS) | ramdisk `default.prop` |

## The 3G sibling is NOT our platform

SM-J105H/B (`j1mini3g`) is 3G SC8830 on a **different kernel platform** — `CONFIG_ARCH_SCX30G`,
`MACH_J1MINI3G`, no `SIPC_LTE`, no `MACH_SP9830I` (see `reference/kernels/android_kernel_samsung_j1mini3g_dmitry/arch/arm/configs/j1mini3g-dt_defconfig`).
The pmOS `samsung-j1mini3g` port is a **reference recipe, not a base** — its kernel config does not match
this hardware.

## Port implications

- **Kernel port base is already correct:** `os/kernel` `j1minilte_linux_defconfig` carries
  `ARCH_SCX35L + MACH_J1MINILTE + MACH_SP9830I + SIPC_LTE` — i.e. the confirmed LTE/SC9830I base.
  The `D1` fallback to `j3xlte/j3xnlte_defconfig` (SC9830) is a safety net only, not the primary base.
- pmOS `samsung-j1minilte` wiki page exists (SC9830, kernel 3.10.65, status "flash, boot bug";
  usbnet/touch/screen working) but **no device/kernel package is merged in pmaports** — we build locally.
- **Hard blocker for phone/data:** the SC9830I LTE modem firmware is closed-source and lives in the CP
  partitions (`l_modem`, `l_fixnv`, `l_runtimenv`, …) — see `docs/plans/modem-firmware-capture-plan.md`.

## Unknowns / gaps (for a 100% pin)

- No IMEI in the dump (`ril.serialnumber=RR8J30F45KL` + `ro.serialno` only; EFS image gitignored).
- No stock-kernel IKCONFIG (exact stock `.config` inferred, not extracted).
- No `l_modem` partition image yet — modem FW version beyond baseband `J105FXXU0APG2` unverified.
- No PIT capture (ROADMAP A3 outstanding — phone in Download Mode needed).
- `dmesg.txt` is a TWRP-kernel boot, not the stock kernel boot.

## Sources

- Local evidence: `device/evidence/` (getprop.txt, byname.txt, cpuinfo.txt, cmdline.txt, dmesg.txt, version.txt, partitions.txt)
- Public dump of the **same firmware build**: `reference/dumps/samsung_j1minilte_dump` (Galaxy-J105F-Resources)
- Web: LPCWiki J1 mini, PhoneDB SM-J105F/DS, SamFw J105FXXS0ARD2 (XID), pmOS wiki `samsung-j1minilte`,
  Bonstra/scx35l_doc, Samsung J320 service manual (SC9830I block diagram)
