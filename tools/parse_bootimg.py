#!/usr/bin/env python3
"""Extract kernel, ramdisk and DTB blob(s) from a Samsung/Spreadtrum Android boot image.

Boot image format (mkbootimg): page-aligned [header][kernel][ramdisk][second][dtb(img)].
The dt.img blob is one of:
  - a raw concatenation of DTBs,
  - a QCDT-style table (dtbTool-sprd output, magic 0xD7B7AB1E),
  - a SPRD table ("SPRD" magic — heads a 0x800-byte area holding up to N
    DTB slots; each 20-byte entry: [u32 tag][u32 index][u32 ?][u32 slot-offset][u32 slot-size]).
DTB magic is big-endian 0xD00DFEED (stored as bytes D0 0D FE ED).
"""

import struct, sys, os


def align(n, page):
    return ((n + page - 1) // page) * page


def read_be32(data, off):
    return struct.unpack_from(">I", data, off)[0]


def main(path, outdir):
    data = open(path, "rb").read()
    assert data[0:8] == b"ANDROID!", "not an Android boot image"
    page_size = struct.unpack_from("<I", data, 36)[0]
    kernel_size = struct.unpack_from("<I", data, 8)[0]
    ramdisk_size = struct.unpack_from("<I", data, 16)[0]
    second_size = struct.unpack_from("<I", data, 24)[0]
    header = data[0:page_size]
    off = page_size
    kernel = data[off : off + kernel_size]
    off += align(kernel_size, page_size)
    ramdisk = data[off : off + ramdisk_size]
    off += align(ramdisk_size, page_size)
    second = data[off : off + second_size]
    off += align(second_size, page_size)
    dtb_blob = data[off:]
    print(
        f"page_size={page_size} kernel={kernel_size} ramdisk={ramdisk_size} second={second_size}"
    )
    print(
        f"kernel magic: {kernel[:4]!r}  ramdisk magic: {ramdisk[:2]!r}  dtb blob starts at 0x{off:x}"
    )
    open(os.path.join(outdir, "kernel_stock.zImage"), "wb").write(kernel)
    open(os.path.join(outdir, "ramdisk_stock.cpio.gz"), "wb").write(ramdisk)

    magics = []
    # QCDT table header magic (Qualcomm-style dt.img; BE magic D7 B7 AB 1E)
    if len(dtb_blob) >= 8 and dtb_blob[0:4] == b"\xd7\xb7\xab\x1e":
        print("dt.img: QCDT table format")
        entry_size = struct.unpack_from("<I", dtb_blob, 8)[0]
        entry_count = struct.unpack_from("<I", dtb_blob, 12)[0]
        for i in range(entry_count):
            base = 16 + i * entry_size
            o, s = struct.unpack_from("<II", dtb_blob, base)
            if o + s <= len(dtb_blob):
                magics.append((o, s, f"qcdt{i:02d}"))
    elif dtb_blob[0:4] == b"SPRD":
        # SPRD table: "SPRD"(4) version(4) count(4), then count entries of
        # 20 bytes: [u32 tag][u32 index][u32 ?][u32 slot_off][u32 slot_sz]
        print("dt.img: SPRD table format")
        entry_count = struct.unpack_from("<I", dtb_blob, 8)[0]
        for i in range(entry_count):
            base = 12 + i * 20
            slot_off = struct.unpack_from("<I", dtb_blob, base + 12)[0]
            slot_sz = struct.unpack_from("<I", dtb_blob, base + 16)[0]
            magics.append((slot_off, slot_sz, f"sprd{i:02d}"))
    else:
        # raw concatenated DTBs: scan for DTB magic (BE) 0xd00dfeed (page aligned)
        idx = 0
        i = 0
        while i + 4 <= len(dtb_blob):
            if dtb_blob[i : i + 4] == b"\xd0\x0d\xfe\xed":
                magics.append((i, None, f"raw{idx:02d}"))
                idx += 1
                i += 4
            else:
                i += 4
    print(f"found {len(magics)} DTB candidate(s)")
    for n, (o, s, tag) in enumerate(magics):
        if s is None:
            nxt = magics[n + 1][0] if n + 1 < len(magics) else len(dtb_blob)
            s = nxt - o
        blob = dtb_blob[o : o + s]
        # DTB total size is at offset 4 (big endian)
        if len(blob) >= 8 and blob[0:4] == b"\xd0\x0d\xfe\xed":
            total = read_be32(blob, 4)
            if 0 < total <= len(blob):
                blob = blob[0:total]
        fn = os.path.join(outdir, f"dtb_{n:02d}_{tag}.dtb")
        open(fn, "wb").write(blob)
        # try to identify the board: strings after the root node
        import re

        strs = re.findall(rb"[ -~]{4,}", blob)
        name = b""
        for s_ in strs:
            low = s_.lower()
            if (
                b"spreadtrum" in low
                or b"sprd" in low
                or b"samsung" in low
                or b"sc98" in low
                or b"sc88" in low
                or b"sp98" in low
            ):
                name = s_
                break
        print(
            f"  {os.path.basename(fn)}: {len(blob)} bytes, id-string: {name.decode('latin1', 'replace')[:80]}"
        )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
