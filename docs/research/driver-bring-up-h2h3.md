# Linux Port — Hardware Bring-up Evidence Pack (H2/H3/H5/H6)

**Date:** 2026-08-14 · **Status:** research/evidence complete — kernel config deltas NOT yet applied (gated on G4 first boot + human approval) · **Scope:** display (H2), touch (H3), zram (H5), USB RNDIS (H6) — the first four hardware items on the ROADMAP H-stage after H1.

Every claim below is grounded in the committed kernel tree (`os/kernel` → `trefeon/linux-samsung-j1minilte`, HEAD `f649d5a5`), live device evidence (`device/evidence/`), or the archived pmOS `samsung-j1mini3g` port (`reference/docs/pmaports/device/archived/`).

---

## 1. H2 — Display (sprdfb framebuffer)

### Driver state (already enabled in `j1minilte_linux_defconfig`)

| Config | Value | Meaning |
|---|---|---|
| `CONFIG_FB_SCX35L=y` | sprdfb driver for the SCX35L LTE family | our SoC family — correct |
| `CONFIG_FB_TRIPLE_FRAMEBUFFER=y` | 3 framebuffers (`/dev/fb0..fb2`) | interacts with the buffering bug below |
| `CONFIG_FRAMEBUFFER_CONSOLE=y` + `CONFIG_VT_CONSOLE=y` | fbcon on `/dev/tty1` | H1's panel shell target |
| `CONFIG_SERIAL_SPRD_UART_CONSOLE=y` | serial console `ttyS1` | evidence channel (Gate D) |

Driver source: `drivers/video/sprdfb/` (`sprdfb_main.c`, `sprdfb_panel.c`, `sprdfb_dsi_panel.c`).

### Panel wiring (device DTS, `arch/arm/boot/dts/sprd-scx35l_sharkls_j1minilte_rev00.dts`)

- Panel node `panel { compatible = "sprd,sprdfb-dsi-panel" }` (line 409) with `gen-panel` + `gen-panel-backlight` + ESD gpio (line 140).
- Backlight: `ktd2801-bl` (`kinetic,backlight-ktd2801`), default brightness step 102→97, max 255→215 (DTS lines ~393-401).
- Panel geometry 480×800 (matches live evidence; touch `max_x=480 max_y=800` confirms).

### Known defect 1 — swapped color channels (MUST fix before claiming H2)

- Root cause: `#define SPRDFB_IN_DATA_TYPE SPRD_IN_DATA_TYPE_ABGR888` at `drivers/video/sprdfb/sprdfb_main.c:67` (enum at line 57). Spreadtrum panels render this default with R/B swapped.
- Fix (proven by archived pmOS port): the committed patch
  `reference/docs/pmaports/device/.shared-patches/linux/sprd/sprdfb-fix-swapped-colors.patch`
  flips the define to `SPRD_IN_DATA_TYPE_BGR565`. Verified against our tree: hunk context matches exactly (same `#define` at line 67, same enum block at 57-62) — applies cleanly, no fuzz.
- Scope: one-line config change to `sprdfb_main.c`.

### Known defect 2 — `sprdfb_check_var()` not buffering-aware (blocks X11/charging-sdl)

- Root cause: `sprdfb_check_var()` in `sprdfb_main.c` rejects `FBIOPUT_VSCREENINFO` when the caller changes `yres_virtual` for a triple-buffered fb (`CONFIG_FB_TRIPLE_FRAMEBUFFER`). Xorg fbdev error observed in the archived port: `(EE) FBDEV(0): FBIOPUT_VSCREENINFO: Invalid argument`.
- Fix (committed reference patch): `sprdfb-check-for-buffering.patch` replaces the `yres_virtual` equality check with a divisibility check (`fb->var.yres_virtual % var->yres_virtual != 0`). Patch description notes the correct long-term fix is comparing against the *incoming* values — the divisibility fix is the accepted pragmatic one.
- Applies to `drivers/video/sprdfb/sprdfb_main.c` ~line 531; context check needed at apply time (H10 milestone — display of X).

### H2 acceptance mapping

1. G4 boot → fbcon on panel: `dmesg | grep -i sprdfb`, `cat /proc/fb`, visible text on `/dev/tty1` (H1 shell).
2. Apply color-swap patch → rebuild → colors correct (red is red). **This changes boot.img checksum — re-run the fail-closed CI verify + re-sync the G4 flash bundle.**
3. Buffering patch deferred to H10 (X11) unless the panel shows corruption earlier.

---

## 2. H3 — Touchscreen (MELFAS MCS8040L, `sec_touchscreen`)

### Driver state (already enabled)

`CONFIG_TOUCHSCREEN_MELFAS_MCS8040L=y` — driver `drivers/input/touchscreen/melfas_mcs8040/mip4.c`.

### Device-tree binding (present in `sprd-scx35l_sharkls_j1minilte_rev00.dts`, i2c1)

```
melfas_mip4@48 {
    compatible = "melfas,mip4_ts";
    reg = <0x48>;
    mip4_ts,irq-gpio = <&d_gpio_gpio 53 0x00>;
    mip4_ts,scl-gpio = <&d_gpio_gpio 93 0x00>;
    mip4_ts,sda-gpio = <&d_gpio_gpio 91 0x00>;
    mip4_ts,max_x = <480>;
    mip4_ts,max_y = <800>;
    mip4_ts,x_num = <4>;
    ...
}
```

### Evidence cross-check (live device)

- `mip4.c:1257` sets `input_dev->name = "sec_touchscreen"` → matches `device/evidence/input_devices.txt` (event2, 480×800, `INPUT_PROP_DIRECT`).
- Same driver (`CONFIG_TOUCHSCREEN_MELFAS_MCS8040L=y`) in the archived pmOS `samsung-j1mini3g` config — **proven working** in that port.
- pmOS wiki: touchscreen confirmed functional on this device family.

### H3 acceptance mapping

1. `evtest /dev/input/event2` → touch events with coordinates in 0..479 / 0..799 (exact 480×800 range proves the driver's `max_x/max_y` are correct).
2. No config delta needed — driver + DTS already in tree. Only verification on-device.
3. If `evtest` missing later: busybox has no evtest — `cat /dev/input/event2 | hexdump` works for raw evidence, or cross-compile `evtest` for the rootfs phase.

---

## 3. H5 — Memory (zram) — CONFIG GAP

- RAM: 941,892 kB (`device/evidence/meminfo.txt`), ~1 GB total.
- Current defconfig: `CONFIG_SWAP=y`, `# CONFIG_ZRAM` **absent** (zram NOT enabled).
- Proven setting: archived j1mini3g config has `CONFIG_ZRAM=y` (+ `CONFIG_SWAP=y`).
- Required delta when H5 opens: add `CONFIG_ZRAM=y` (+ `CONFIG_ZRAM_DEBUG` optional) to `j1minilte_linux_defconfig`. With 1 GB RAM, ~256–512 MB zram swap is the sensible first value (`/sys/block/zram0/disksize`, then `mkswap`/`swapon` in initramfs or rootfs).
- Why mandatory: 3.10 + XFCE4 on 1 GB without swap will OOM during the desktop phase (H10/H11). ROADMAP H5 explicitly calls this out.

---

## 4. H6 — USB RNDIS (debug networking) — CONFIG OPTION

### Current state

`CONFIG_USB_GADGET=y`, `CONFIG_USB_G_ANDROID=y`, `CONFIG_USB_G_ANDROID_SAMSUNG_COMPOSITE=y`, `CONFIG_USB_F_ACM=y`. **No** `CONFIG_USB_CONFIGFS` in this 3.10 tree (gadget configfs support not present — verified: no `USB_CONFIGFS` in `drivers/usb/gadget/Kconfig`).

### Two proven paths (both use in-tree code)

1. **Android composite RNDIS** (recommended, matches stock): `drivers/usb/gadget/android.c` compiles in `f_rndis.c` + `rndis.c` (`android.c:48-50`) with a `rndis_function` (`android.c:606`). Function set is switched at runtime via `/sys/class/android_usb/android0/functions` (e.g. `rndis`, `adb`, `acm`). The pmOS wiki confirms usbnet works on this family via this mechanism (telnet in initramfs / SSH in rootfs over USB).
2. **g_ether** (`CONFIG_USB_ETH=y` + `CONFIG_USB_ETH_RNDIS=y`, `drivers/usb/gadget/Kconfig:619,655`): single-configuration gadget, zero userspace wiring — simplest for an initramfs debug channel.

### H6 acceptance mapping

1. Enable the chosen option (recommended: add `CONFIG_USB_ETH=y` + `CONFIG_USB_ETH_RNDIS=y` for the initramfs debug path — one config line, no sysfs wiring; keep `G_ANDROID` for later Android-compat needs).
2. Host side: `usb0` appears, `ip addr add 192.168.42.1/24 dev usb0`, ping the device (`192.168.42.129` stock convention). Initramfs must bring up `usb0` + a static IP at H6 time.
3. Wi-Fi (`sprdwl`/`sc2331`) stays "unsupported" until actual association — RNDIS is the declared primary link (ROADMAP R7, D-6).

---

## 5. Config delta summary (apply only when the gate opens)

| Milestone | Change | Where | Size risk |
|---|---|---|---|
| H2 | sprdfb color swap: `SPRD_IN_DATA_TYPE_BGR565` | `sprdfb_main.c:67` (one line) | none — code-only, image size unchanged |
| H2 (H10) | sprdfb check_var buffering fix | `sprdfb_main.c` ~531 | none |
| H5 | `CONFIG_ZRAM=y` (+ zram-utils in rootfs) | defconfig | zram is a module of ~tens of KB; verify < 16 MiB |
| H6 | `CONFIG_USB_ETH=y` + `CONFIG_USB_ETH_RNDIS=y` | defconfig | small; verify < 16 MiB |

Every config/code delta above changes the boot.img checksum → the fail-closed CI verify (header/size/dt.img) plus a fresh SHA256SUMS run is mandatory, and the G4 flash bundle at `device/evidence/build-artifacts/kernel-m31/` must be re-synced before it is flashed (same discipline as the 2026-08-14 artifact corrections).

---

## 6. Sources

- Kernel tree: `os/kernel` (`drivers/video/sprdfb/`, `drivers/input/touchscreen/melfas_mcs8040/mip4.c`, `arch/arm/boot/dts/sprd-scx35l_sharkls_j1minilte_rev00.dts`, `arch/arm/configs/j1minilte_linux_defconfig`, `drivers/usb/gadget/{android.c,Kconfig}`).
- Device evidence: `device/evidence/` (`input_devices.txt`, `meminfo.txt`).
- Archived pmOS port: `reference/docs/pmaports/device/archived/{device,linux}-samsung-j1mini3g/` (deviceinfo, config-samsung-j1mini3g.armv7, sprdfb patches).
- Shared patches: `reference/docs/pmaports/device/.shared-patches/linux/sprd/`.
- pmOS wiki (samsung-j1mini3g/j1minilte pages): usbnet + touchscreen working; device package not merged in pmaports — local build required (consistent with ROADMAP §1 and `exact-model-findings.md`).
