# LTE Modem Firmware Capture Plan (pre-flash prerequisite)

**Date:** 2026-08-14 · **Status:** planned — capture requires the phone (HUMAN GATE) · **Why now:** model confirmed as SM-J105F/DS **SC9830i LTE** (`docs/research/exact-model-findings.md`); the LTE modem firmware is **closed-source** and lives only in the CP partitions — it is **not** in the `/system` dump and **not** yet in our rollback set.

## Why this matters

1. **Rollback completeness (risk R2/R5):** the A2 rollback set covers RECOVERY (p21), KERNEL (p20), efs (p17), prodnv (p18) — but **not** the modem CP set. A bad flash or EFS/cp corruption could leave the phone with working recovery but dead radio, with no way back.
2. **Linux/pmOS port (Phase 3/4):** phone/data on the Linux port requires the proprietary CP firmware + `modemd`/`wcnd` blobs. The pmOS `j1mini3g` port got archived partly because wifi needed proprietary blobs; our LTE CP is harder. We must capture the modem partitions while the phone still has them intact.
3. **Baseband version evidence:** current baseband `J105FXXU0APG2` is only a string; the actual FW in `l_modem` is unverified.

## Partitions to capture (authoritative — `device/evidence/byname.txt` + `partitions.txt`)

All sizes from `/proc/partitions` (KiB → bytes ×1024). **LTE CP set** (prefix `l_`) + TD-set (`td_`) + supporting NV:

| Partition | Device | Size (KiB) | Size (B) | Status |
|---|---|---|---|---|
| `l_modem` | mmcblk0p8 | 16,384 | 16,777,216 | ❌ NOT captured |
| `l_ldsp` | mmcblk0p7 | 4,096 | 4,194,304 | ❌ NOT captured |
| `l_gdsp` | mmcblk0p9 | 4,096 | 4,194,304 | ❌ NOT captured |
| `l_warm` | mmcblk0p10 | 4,096 | 4,194,304 | ❌ NOT captured |
| `l_fixnv1` | mmcblk0p3 | 1,024 | 1,048,576 | ❌ NOT captured |
| `l_fixnv2` | mmcblk0p4 | 1,024 | 1,048,576 | ❌ NOT captured |
| `l_runtimenv1` | mmcblk0p12 | 1,024 | 1,048,576 | ❌ NOT captured |
| `l_runtimenv2` | mmcblk0p13 | 1,024 | 1,048,576 | ❌ NOT captured |
| `td_runtimenv1` | mmcblk0p14 | 1,024 | 1,048,576 | ❌ NOT captured |
| `td_runtimenv2` | mmcblk0p15 | 1,024 | 1,048,576 | ❌ NOT captured |
| `pm_sys` | mmcblk0p5 | 1,024 | 1,048,576 | ❌ NOT captured |
| `rsvdfixnv1` | mmcblk0p6 | 1,024 | 1,048,576 | ❌ NOT captured |
| `prodnv` | mmcblk0p18 | 5,120 | 5,242,880 | ✅ A2 (stock-backup/) |
| `efs` | mmcblk0p17 | 20,480 | 20,971,520 | ✅ A2 (stock-backup/) |

Total to add: **12 partitions, 33,554,432 B (32 MiB)**.

> Note: `l_fixnv` / `l_runtimenv` hold calibration/NV (IMEI-linked) data — treat as sensitive; never publish. `l_modem` may contain vendor firmware blobs — keep local, do not commit (same gitignore discipline as the `.img` files in `stock-backup/`).

## Capture commands (from TWRP, phone connected — HUMAN GATE)

Run from the existing TWRP 3.7.0 session (Method A, same pattern as A2). `$adb` = `D:\github_repo\Project_J105F\tools\platform-tools\adb.exe` (or `C:\adb\adb.exe`).

```powershell
# per partition, to the microSD first (survives reboots), then pull to PC
$parts = @(
  "l_modem:8", "l_ldsp:7", "l_gdsp:9", "l_warm:10",
  "l_fixnv1:3", "l_fixnv2:4", "l_runtimenv1:12", "l_runtimenv2:13",
  "td_runtimenv1:14", "td_runtimenv2:15", "pm_sys:5", "rsvdfixnv1:6"
)
foreach ($p in $parts) {
  $name, $num = $p.Split(":")
  & $adb shell "dd if=/dev/block/mmcblk0p$num of=/external_sd/backup/${name}.img bs=4096"
}
& $adb shell "ls -l /external_sd/backup/"
# pull everything to PC:
& $adb pull /external_sd/backup/ device/evidence/stock-backup/
```

Verify **size + SHA-256** on PC for each (sizes must match the table above exactly; a mismatch means the partition layout assumption is wrong — stop and re-check byname.txt):

```powershell
Get-ChildItem device/evidence/stock-backup/l_*.img, device/evidence/stock-backup/td_*.img,
  device/evidence/stock-backup/pm_sys.img, device/evidence/stock-backup/rsvdfixnv1.img |
  ForEach-Object { "$($_.Name) $($_.Length) $((Get-FileHash $_.FullName -Algorithm SHA256).Hash)" }
```

Append the 12 rows to `device/evidence/stock-backup/CHECKSUMS.sha256` (committed metadata; images stay gitignored).

## PIT capture (A3 — closes the last ROADMAP gap)

While the phone is available, also capture the PIT (partition table). Requires **Download Mode** (not TWRP):

```powershell
# phone: Power off → VolDown+Home+Power → Download Mode → connect USB
# heimdall 1.4.2 (needs the Samsung USB driver / Zadig):
heimdall print-pit --no-reboot --output device/evidence/pit/j105f.pit
# (or heimdall print-pit --verbose and record the output table)
```

PIT gives the authoritative partition geometry + GPT check for `byname.txt`. It is optional (A3 is already satisfied by `/proc/partitions` + byname) but closes the loop and cross-checks sizes.

## Sequencing (when the phone returns)

1. **Capture modem set first** (this plan) — before any E2 recovery or G4 kernel flash, so rollback covers the radio too.
2. Re-verify stock-backup CHECKSUMS (all 16 images incl. the new 12).
3. Only then proceed to E2 (custom recovery flash) / G4 (kernel flash) per ROADMAP.
4. Restore if ever needed: `dd if=/external_sd/backup/l_modem.img of=/dev/block/mmcblk0p8 bs=4096` etc. (same pattern as stock-backup README).

## Evidence artifacts

- `device/evidence/stock-backup/{l_modem,l_ldsp,l_gdsp,l_warm,l_fixnv1,l_fixnv2,l_runtimenv1,l_runtimenv2,td_runtimenv1,td_runtimenv2,pm_sys,rsvdfixnv1}.img` (gitignored)
- `device/evidence/stock-backup/CHECKSUMS.sha256` (updated, committed)
- `device/evidence/pit/j105f.pit` (committed if captured)
