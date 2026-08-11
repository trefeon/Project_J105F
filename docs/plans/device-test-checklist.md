# Phase 2 — Device Test Checklist (SM-J105F custom TWRP)

Status: READY — awaiting device + user approval (FR-5: no flashing without explicit approval).

## 0. Preconditions (safety net — MUST be done first)

- [ ] Stock recovery preserved + checksummed: `device/evidence/stock-backup/recovery_stock.img` (re-verify SHA-256)
- [ ] Working TWRP 3.0.3-0 tar preserved (rollback) — checksum recorded
- [ ] Nandroid backup of EFS/BOOT/SYSTEM/DATA/CACHE verified restorable (from Phase 0 of the Linux plan)
- [ ] USB cable + Odin 3.13.1 ready; device can reach download mode (Vol-Down + Home + Power)
- [ ] Current custom `recovery.img` SHA-256 recorded (from CI SHA256SUMS)

## 1. Flash (user-approved only)

- [ ] Flash `recovery.tar` via Odin AP slot **or** `dd` from existing recovery
  - `dd if=/sdcard/recovery_custom.img of=/dev/block/mmcblk0p21` (RECOVERY partition; verify partition number from `by-name`)
- [ ] Boot into new recovery (Vol-Up + Home + Power)
- [ ] Record which method was used + outcome

## 2. Functionality matrix (Task 2.2)

| # | Item | Expected | Result |
|---|---|---|---|
| 2.1 | Boot to TWRP home | UI renders, no garble | |
| 2.2 | Touchscreen | swipe/tap works | |
| 2.3 | Display orientation | correct (portrait) | |
| 2.4 | Brightness | slider 0..255 works | |
| 2.5 | Reboot → system / download mode | both work | |
| 2.6 | Key mapping (power/vol keys) | expected actions | |
| 2.7 | ADB shell | `adb devices` + root shell | |
| 2.8 | MTP | files visible on PC | |
| 2.9 | Mount /system, /data, /cache, internal storage, external SD | all mount | |
| 2.10 | Backup + restore | full nandroid round-trip | |
| 2.11 | Insufficient-space backup | clean error, no crash | |
| 2.12 | Encryption | document behavior (expect unsupported on this device) | |
| 2.13 | About screen | shows `0_j105f-custom` version | |

## 3. Rollback test (Task 2.3)

- [ ] Flash stock recovery back via Odin → boots to stock recovery
- [ ] Flash custom back → boots again
- [ ] Record both outcomes

## 4. Evidence to capture

- Photos of boot/TWRP screens where possible
- `dmesg` / recovery log via ADB (`adb pull /tmp/recovery.log`)
- SHA-256 of the final working image
- Save final image as `device/evidence/stock-backup/recovery_custom.img` + commit checksum

## Gate C (PRD): after this passes, the custom TWRP milestone is shippable.
