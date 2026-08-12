# Stock rollback set (local only — gitignored)

Rollback images dumped 2026-08-12 via TWRP 3.7.0_9-0-notnoelchannel from the tested unit
(SM-J105F, `j1minilte`/`j1miniltexx`, sc8830, PDA `J105FXXS0ARD2`).
Sizes verified against the authoritative partition table (`device/evidence/partitions.txt`):
**recovery/boot = exactly 16,777,216 B (16 MiB)** — matches the ROADMAP A3/A4 value.

| Image | Partition | Device | Size (B) |
|---|---|---|---|
| `recovery_stock.img` | RECOVERY | `mmcblk0p21` | 16,777,216 |
| `boot_stock.img` | KERNEL | `mmcblk0p20` | 16,777,216 |
| `efs.img` | efs | `mmcblk0p17` | 20,971,520 |
| `prodnv.img` | prodnv | `mmcblk0p18` | 5,242,880 |

## Restore commands (from TWRP, image on microSD)

```sh
dd if=/external_sd/backup/recovery_stock.img of=/dev/block/mmcblk0p21 bs=4096
dd if=/external_sd/backup/boot_stock.img     of=/dev/block/mmcblk0p20 bs=4096
dd if=/external_sd/backup/efs.img            of=/dev/block/mmcblk0p17 bs=4096
dd if=/external_sd/backup/prodnv.img         of=/dev/block/mmcblk0p18 bs=4096
```

## Provenance

- Checksums: `CHECKSUMS.sha256` (committed — this file; the `.img` files themselves are gitignored).
- These images are the A2 rollback set (risks R2/R5). Nothing gets flashed until they exist —
  they now do, locally and on the microSD.
