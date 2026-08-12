# E1/E2 — Flash and rollback commands (custom recovery)

For the E-stage device session. All of these are **read twice by the human before anything is flashed**.
Never flash without the human's explicit "yes" in the same session (ROADMAP hard rule).

## 0. Pre-flight assertions (E1)

Run from TWRP (device connected, `adb devices` shows `recovery`):

```powershell
$adb = "D:\github_repo\Project_J105F\tools\platform-tools\adb.exe"
& $adb shell "getprop ro.product.device; getprop ro.build.PDA"
```

Expected (risk R3 control):
- `ro.product.device` = `j1minilte`
- `ro.build.PDA` = `J105FXXS0ARD2`

Target partition: **RECOVERY = `/dev/block/mmcblk0p21`, exactly 16,777,216 B** (16 MiB).
Rollback images exist at `device/evidence/stock-backup/` (PC) and `/external_sd/backup/` (microSD),
checksummed in `device/evidence/stock-backup/CHECKSUMS.sha256` (committed).

Image to flash: `device/evidence/build-artifacts/twrp-j1minilte/recovery.img`
(11,890,688 B, sha256 `9869d726…` — under the 16 MiB gate; header pgsz 2048, offsets per ROADMAP §1).

## 1. Flash the custom recovery

### Method A — from the existing TWRP (preferred, least destructive)

```powershell
$adb = "D:\github_repo\Project_J105F\tools\platform-tools\adb.exe"
& $adb push device/evidence/build-artifacts/twrp-j1minilte/recovery.img /external_sd/recovery_new.img
& $adb shell "dd if=/external_sd/recovery_new.img of=/dev/block/mmcblk0p21 bs=4096"
# verify the flash read-back (optional but cheap):
& $adb shell "dd if=/dev/block/mmcblk0p21 bs=4096 2>/dev/null | sha256sum"
# must print: 9869d7268bd57bc37c5c4e1d3a51b0c84d4ee43e2ff621903eaa3837eb55c05a
```

(Alternative GUI route: TWRP → Install → Install Image → select `recovery_new.img` → partition: **RECOVERY** → swipe.)

### Method B — Odin/AP (fallback)

`recovery.tar` (plain) or `recovery.tar.md5` (Odin classic) from
`device/evidence/build-artifacts/twrp-j1minilte/`. Odin version used for the successful flash
must be recorded here (D-2 resolution):

```
Odin version: ______ (fill after the successful flash)
```

## 2. First boot (E2)

- Reboot to recovery: `adb reboot recovery` (or VolUp+Home+Power).
- **Success:** TWRP UI boots; About screen shows `0_j105f-custom` / "Samsung Galaxy J1 Mini (custom TWRP)".
  Photograph the About screen.
- **Rollback trigger:** no display, no touch, or repeated boot loop → immediately do step 3.

## 3. Rollback (proven path, images checksummed)

```powershell
# images already on the microSD at /external_sd/backup/ (or re-push from PC):
$adb = "D:\github_repo\Project_J105F\tools\platform-tools\adb.exe"
& $adb push device/evidence/stock-backup/recovery_stock.img /external_sd/recovery_stock.img
& $adb shell "dd if=/external_sd/recovery_stock.img of=/dev/block/mmcblk0p21 bs=4096"
& $adb shell "dd if=/dev/block/mmcblk0p21 bs=4096 2>/dev/null | sha256sum"
# must print: 6279f91243653717fe061bc5ff87c60a814b06d6a0bdee76e01625f87a743116
& $adb reboot recovery
```

Stock image is exactly 16,777,216 B; the read-back checksum proves the restore.

## 4. E3 matrix afterwards

Run the test matrix from `docs/plans/device-test-checklist.md`; record verdicts in
`docs/delivery/recovery-test-matrix.md` (create on execution). Anything failing = documented known
limitation, never silently presented as working.