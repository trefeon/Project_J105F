# Project J105F — Product Requirements

## Product goal

Deliver a trustworthy custom recovery for the Samsung SM-J105F and establish a separately tracked path toward a bootable Linux/pmOS port. The recovery is the first shippable milestone; Linux remains experimental until hardware bring-up evidence exists.

## Users and use cases

- **Owner/operator:** boots recovery, uses ADB/MTP, mounts storage, backs up/restores the phone, and can recover using stock images.
- **Developer:** rebuilds the recovery from committed device/kernel source and receives traceable CI artifacts.
- **Linux porter:** uses verified hardware evidence, kernel logs, DTBs, and boot parameters to advance the pmOS port without confusing a kernel compile with device support.

## Scope

### MVP: custom TWRP

- Build from an upstream TWRP base plus this repository's committed device tree and kernel.
- Produce a bootable `recovery.img` and Odin-compatible `recovery.tar`.
- Identify the build with project branding, source commit, manifest revision, and checksums.
- Support the tested `j1miniltexx` / `sc8830` variant only unless another variant is explicitly validated.
- Verify display, touch, brightness, ADB, MTP, storage mounts, backup/restore, reboot/download mode, and rollback.

### Follow-on: Linux/pmOS

- Build a documented kernel baseline.
- Boot to a debug shell.
- Bring up display, touch, storage, USB/debug, power, and other hardware incrementally.
- Publish limitations and unsupported firmware/hardware clearly.

## Non-goals

- No clone script as the product implementation.
- No automatic device flashing.
- No claim of universal SM-J105F/J105 variants without per-variant evidence.
- No production-quality Linux claim before repeated boots and core hardware tests.

## Functional requirements

### FR-1 Source ownership

The device tree and target kernel used by CI MUST be read from this repository's committed `device/samsung/j1minilte` and `kernel/samsung/j1minilte` paths. External downloads are permitted only for the declared upstream base and toolchain.

### FR-2 Reproducible build

A clean GitHub Actions runner MUST be able to resolve the pinned/recorded build inputs, build the recovery, and retain logs on failure.

### FR-3 Artifact safety

CI MUST reject a recovery image larger than the target 20 MiB recovery partition and MUST publish SHA-256 checksums and build metadata.

### FR-4 Recovery behavior

The recovery MUST boot on the tested device and provide working display, touch, ADB shell, MTP, storage mounts, backup/restore, and reboot/download mode. Any unsupported capability MUST be documented and visible in the release notes.

### FR-5 Rollback

Before device testing, stock recovery and the currently working recovery MUST be preserved and checksummed. The flash procedure MUST include a documented rollback path.

### FR-6 Linux evidence

Each Linux milestone MUST include the exact source revision, config, toolchain, image checksum, boot log, and a statement of tested hardware behavior.

## Quality requirements

- No secrets, private dumps, modem data, or unreviewed proprietary blobs in Git.
- Build failures identify the earliest actionable error.
- Recovery and Linux status are reported as separate milestones.
- Documentation is sufficient for another developer to reproduce the build and recover the device.

## Acceptance gates

### Gate A — CI source/layout

- Local device/kernel paths are tracked and copied successfully.
- CI contains no external clone of the device tree/kernel.

### Gate B — Recovery artifact

- Clean runner produces a size-valid `recovery.img` and `recovery.tar`.
- Checksums and build metadata are retained.

### Gate C — Device validation

- Tested device identity matches the supported variant.
- Core recovery test matrix passes and rollback is demonstrated or explicitly deferred with a reason.

### Gate D — Linux experimental milestone

- Kernel reaches a reproducible debug point.
- Three boot attempts and logs are recorded for each claimed milestone.

## Open decisions

- Pin exact TWRP manifest revision after the first successful clean sync.
- Decide whether the final release uses a patched Odin TAR/MD5 convention or a plain TAR accepted by the tested Odin version.
- Decide the minimum Linux hardware set for the first public experimental release.
