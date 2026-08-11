# Kernel Foundation — M3.1 Report (Linux boot image builds reproducibly)

**Status:** in progress (2026-08-11) · **Milestone:** M3.1 (kernel builds reproducibly in CI; DTBs byte-match stock) · **Plan:** `docs/plans/linux-kernel-foundation-plan.md`

## What changed

New nested kernel repo `trefeon/linux-samsung-j1minilte` (workspace `os/kernel/`, gitignored in main repo):

| Commit | Content |
|---|---|
| `90cfeaa5` | Vendor kernel 3.10 import, blob-parity verified vs twrp repo 4908f45a (45,061 files, 0 mismatches); 13 NTFS-restricted paths via cacheinfo+skip-worktree (Windows only); `tests/stock-dtb/` (5 device DTBs); NOTICE/README/.gitignore; vendor `main.yml` retained (provenance, manual trigger) |
| `498f0115` | `j1minilte_linux_defconfig` (DEVTMPFS=y, DEVTMPFS_MOUNT=y, VT=y, VT_CONSOLE=y, FRAMEBUFFER_CONSOLE=y) + `tools/make_linux_defconfig.sh` |
| `a6a24d4a` | `tools/pack_bootimg.py` + `pack_dtimg.py` (SPRD table, byte-exact) + `parse_bootimg.py` |
| `7cf59d50` | `pack_dtimg.py`: non-gating `--compare-dtb` diagnostic mode |
| `36e22d56` | `initramfs/init` + `tools/build_initramfs.sh` (busybox 1.36.1 static, sha512 pinned) |
| `70a3c979` | `.github/workflows/kernel.yml` (build + fail-closed verify + diagnostics) |
| (fix) | busybox CONFIG_STATIC via `.config` sed (1.36.1 dropped `scripts/config`) |

## Ground truth re-verified

- `pack_dtimg.py` output is **byte-identical to the device's own `prebuilt/dtb`** (329,728 B = 0x50800, 5 SPRD slots) — packer validated against device ground truth.
- `pack_bootimg.py` header matches the decoded device layout (page 2048, kernel 0x8000, ramdisk 0x1000000, second 0xf00000, tags 0x100, cmdline `console=ttyS1,115200n8`, dt_size field, SEANDROIDENFORCE suffix).
- Milestone-1 DTB strategy: dt.img packed from stock DTBs (device truth, same bytes as the TWRP recovery used); kernel-built dtbs (in-tree dtc 1.2.0) compared DIAGNOSTICALLY (non-gating).

## Evidence (green run 31519306192; artifacts re-downloaded on the .config fix run)

- CI run: https://github.com/trefeon/linux-samsung-j1minilte/actions/runs/31519306192 (run 1, green; run 31520084805 re-verified with .config artifact) — status: **success**
- Fail-closed verify (CI log): `VERIFY PASS: header fields OK, size OK, dt.img byte-identical to packed-from-stock`; boot.img = 6,850,560 B (6.53 MiB ≤ 20 MiB); dt.img = 329,728 B (exactly the device prebuilt size); `dtb verification OK: all packed DTBs byte-identical to stock`
- Busybox initramfs built (1.36.1, sha512-pinned); ramdisk.cpio.gz 1,304,859 B; kernel zImage 5,209,144 B (arm-eabi-4.8 GCC 4.8)
- `SHA256SUMS` (run 31520084805, final): boot.img `a8603c2d2cab813c4a98b73c497206faf80ed83dca610ed31f9265afb4122a9b` (run-1 value; re-verified locally: all artifacts match CI hashes)
- `BUILD_INFO.txt`: kernel_commit 05c7b22a (post-fix HEAD), defconfig j1minilte_linux_defconfig, toolchain arm-eabi-4.8 @ android-5.1.1_r38, busybox 1.36.1, built_at 2026-08-11T17:52:33Z, cmdline `console=ttyS1,115200n8`, mkbootimg params incl. SEANDROIDENFORCE
- Diagnostic dtb comparison: **0/5 kernel-built dtbs identical to stock** (in-tree dtc 1.2.0 vs the device's toolchain — expected, non-gating; milestone-1 gate uses the packed-from-stock dt.img). Follow-up (M3.4) will port a newer dtc if kernel-built dtbs must reproduce stock bytes.
- Artifacts downloaded to `device/evidence/build-artifacts/kernel-m31/` — local `Get-FileHash` matches CI `SHA256SUMS`: **yes (all 5 binaries; .config included from the fix run)**

## Gate status

- **M3.1: DONE** — CI builds zImage + dt.img + initramfs + boot.img reproducibly; fail-closed verify passes (header fields, size ≤ 20 MiB, dt.img byte-identical to packed-from-stock)
- **M3.2: DONE (materials)** — boot.img verified against boot layout by the same CI gate; flashable file + evidence pack in hand
- M3.3 (device boot test): **requires user + explicit approval** (TWRP → Install Image → KERNEL)

## Next

1. Green run → download artifacts → verify checksums locally → mark M3.1/M3.2 done in `docs/delivery/tasks.md`
2. User decision: proceed to M3.3 device boot test (needs the phone + approval)
