# Execution Log

Protocol per `docs/delivery/ROADMAP.md` §0 item 4: append one row per completed task:

`<TASK-ID> | <ISO date> | done|blocked | <one-line result> | <commit sha or artifact ref>`

Rows for tasks completed before this file existed were reconstructed from the ROADMAP checkboxes,
the git history, and CI run metadata on 2026-08-12.

| Task | Date | Status | Result | Ref |
|---|---|---|---|---|
| A1 | 2026-08-11 | done | ROADMAP committed as the execution spine; supersede banners + corrections C2/C3/C4 applied inline | `64ae684` |
| A2 | 2026-08-12 | done | Rollback set created: dd of p21/p20/p17/p18 → PC `stock-backup/` (recovery/boot exactly 16,777,216 B — stop rule passed; efs 20 MiB, prodnv 5 MiB match table); CHECKSUMS.sha256 + README committed; TWRP backup System 2.09 GB + Data 1.29 GB (.sha2) pulled to PC; cmdline/dmesg/df re-captured real (`console=null`, bootloader J105FXXS0ARD2); TWRP identified as 3.7.0_9-0-notnoelchannel | `stock-backup/` (gitignored imgs), run `db9a2d6b` |
| A3 | 2026-08-11 | blocked | Live `/proc/partitions` applied as C4 (p20/p21 = 16,384 KiB); heimdall PIT capture outstanding (needs phone in Download Mode) | `device/evidence/partitions.txt` |
| A4 | 2026-08-11 | done | BoardConfig BOOT+RECOVERY partition sizes 16777216 with evidence comment | twrp `0f7f3586` |
| A4b | 2026-08-11 | done | kernel.yml size gate tightened to 16777216 (fail closed) | kernel `f31f090a` |
| B1 | 2026-08-11 | done | Python 2 blocker fixed via source-built 2.7.18 + libncurses5; build advanced past `lunch` | run `31465251155` |
| B2 | 2026-08-11 | done | recovery.img produced; 6 root causes fixed one per iteration (docs/build-reports/ci-investigation.md) | runs `31469647748`/`31472573689`/`31474055688` |
| B3 | 2026-08-11 | done | Pre-build kernel assertions: defconfig, arm-eabi-gcc, prebuilt DTB | twrp workflow |
| C1 | 2026-08-11 | done | Fail-closed ≥ 16 MiB gates in both repos; R1 closed; green runs re-verified | `0f7f3586` + `f31f090a`; runs `31524994619`/`31524994372` |
| C2 | 2026-08-11 | done | SHA256SUMS + BUILD_INFO.txt + manifest-pinned.xml published with TWRP and kernel artifacts | `build-artifacts/` |
| C3 | 2026-08-12 | done | `recovery.tar.md5` created and verified (tar + 32-char MD5 appended, delta 32 B, re-hash matches `6ba01d34…`); `tar -tf` lists exactly `recovery.img`. Odin version naming stays open until E2 | `build-artifacts/twrp-j1minilte/recovery.tar.md5` |
| D1 | 2026-08-11 | done | Branding `0_j105f-custom` + PRODUCT_MODEL; strings verified in final ramdisk | twrp `2d63e410` |
| D2 | 2026-08-11 | done | AGPL COPYING preserved; NotNoelChannel attribution explicit | twrp README |
| D3 | 2026-08-11 | deferred | Optional splash polish; headroom exists under the C1 gate | — |
| E1 | 2026-08-12 | blocked | Pre-flight parse recorded: pgsz 2048, kernel 5,146,640 B, ramdisk 6,408,655 B, DTB blob @ 0xb06800, 5× DTBs SP8835EB (byte-identical sizes vs stock). Remaining checks + flash need A2 rollback set + `HUMAN GATE` | `build-artifacts/twrp-j1minilte/parsed-e1/` |
| G1 | 2026-08-11 | done | CI-first host decision (D5); kernel builds reproducibly on ubuntu-22.04 | kernel repo |
| G2 | 2026-08-11 | done | Kernel forked to `trefeon/linux-samsung-j1minilte` (vendor tree, K1) | `90cfeaa5` |
| G3 | 2026-08-11 | done | boot.img 6.53 MiB assembled in CI; fail-closed VERIFY PASS (header/size/dt.img byte-identical) | runs `31519306192`/`31520084805` |
| G4 | 2026-08-11 | blocked | First kernel flash attempt — rollback set now READY (A2 done 2026-08-12); awaiting human approval for the flash session (`HUMAN GATE`); restore `boot_stock.img` to p20 for rollback | — |

**Next actionable items:** A3 (heimdall PIT, phone in Download Mode — optional, `partitions.txt` already authoritative) → E2 flash of custom recovery (human "yes" required) → G4 kernel flash (human "yes" required).
