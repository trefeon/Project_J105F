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

**Next actionable items:** (phone absent) → on phone return: capture LTE modem CP set (`docs/plans/modem-firmware-capture-plan.md`) → A3 heimdall PIT (Download Mode — optional) → E2 flash of custom recovery (human "yes") → G4 kernel flash (human "yes").

**2026-08-14 (exact-model research, no phone):** two parallel research lanes (local-dump mining + web) confirmed the unit as **SM-J105F/DS LTE** — SoC **SC9830i** (SharkLS, SCX35L family), board SP8835EB, 1 GB RAM; `sc8830` strings are the platform-family name, **not** the 3G chip; the 3G sibling `j1mini3g` (SM-J105H/B) is a different kernel platform (`ARCH_SCX30G`), reference recipe only. Artifacts: `docs/research/exact-model-findings.md` (new), stale `SC8830-as-chip` claims corrected in `docs/research/J105F-CustomOS-Research.md`, kernel README identity section (kernel repo `73a2f74a`), ROADMAP identity row clarified, `docs/plans/modem-firmware-capture-plan.md` (new — 12 CP partitions to capture pre-flash).

| H1 | 2026-08-14 | done | Debug initramfs boots to shell: init mounts basics + writes Gate-D boot evidence to serial, interactive shell on ttyS1 (PID 1) + tty1 (setsid -c) when fbcon up; CI fail-closed verifies initramfs (init + sh -n + static busybox 1.36.1); stripped vendor CMDLINE mem=128M landmine; boot.img 6,850,560 B < 16 MiB; all checksums verified locally | kernel `f649d5a5`, run `31799705308`, boot.img `e3125677…` |

**2026-08-14 (H2/H3/H5/H6 research pack, no phone):** `docs/research/driver-bring-up-h2h3.md` committed — sprdfb color-swap fix (`sprdfb_main.c:67` ABGR888→BGR565, archived patch applies cleanly) + check_var buffering fix (H10); MELFAS MCS8040L touch (`mip4.c:1257` registers `sec_touchscreen`, DTS binding `melfas_mip4@48` on i2c1 with 480×800) — driver already enabled, no delta; zram **gap** (`CONFIG_ZRAM` absent vs proven `y` in archived j1mini3g config); RNDIS: android composite `rndis_function` in-tree + `CONFIG_USB_ETH`+`USB_ETH_RNDIS` recommended (no gadget configfs in this 3.10 tree). Config deltas deferred to the G4 gate.

**2026-08-14 correction (C3/E1 artifacts):** the `twrp-j1minilte/` bundle (recovery.img + recovery.tar + recovery.tar.md5) was discovered to contain a **stale first-green image** — hash `9869d726`, run `31469647748`, commit `dfccd4fb`, **pre-branding** (`0_j1mini_custom` in ramdisk). Replaced with the gated HEAD artifact `799b5e10` (run `31524994619`, commit `0f7f3586`, branding `0_j105f-custom`); `recovery.tar` + `recovery.tar.md5` rebuilt from it (md5 `52067f65…`). `e1-flash-commands.md` corrected accordingly. Stock rollback images untouched.

**2026-08-14 correction (G3/kernel bundle):** `kernel-m31/` flash bundle re-synced from pre-gate run `31519306192` (boot.img `a8603c2d`, commit `05c7b22a`) to the gate-verified HEAD run `31524994372` (boot.img `671a576a`, commit `f31f090a`). Kernel source identical (top-3 commits workflow-only); dt.img unchanged (`f29f3d90…`).
