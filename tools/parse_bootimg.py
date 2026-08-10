#!/usr/bin/env python3
"""Extract kernel, ramdisk and DTB blob(s) from a Samsung/Spreadtrum Android boot image.

Boot image format (mkbootimg): page-aligned [header][kernel][ramdisk][second][dtb(img)].
The dt.img blob is either a raw concatenation of DTBs or a QCDT-style table
(dtbTool-sprd output, used with deviceinfo_bootimg_qcdt=true).
"""

import struct, sys, os


def align(n, page):
    return ((n + page - 1) // page) * page


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
    # QCDT table header magic (Qualcomm-style dt.img)
    if len(dtb_blob) >= 8 and struct.unpack_from("<I", dtb_blob, 0)[0] == 0xD7B7AB1E:
        print("dt.img: QCDT table format")
        total = struct.unpack_from("<I", dtb_blob, 4)[0]
        entry_count = struct.unpack_from("<I", dtb_blob, 12)[0]
        entry_size = struct.unpack_from("<I", dtb_blob, 8)[0]
        for i in range(entry_count):
            base = 16 + i * entry_size
            off, size = struct.unpack_from("<II", dtb_blob, base)
            if off + size <= len(dtb_blob):
                magics.append((off, size, f"qcdt{i:02d}"))
    else:
        # raw concatenated DTBs: scan for DTB magic 0xd00dfeed (page aligned)
        idx = 0
        i = 0
        while i + 4 <= len(dtb_blob):
            if struct.unpack_from("<I", dtb_blob, i)[0] == 0xD00DFEED:
                magics.append((i, None, f"raw{idx:02d}"))
                idx += 1
                i += 4
            else:
                i += 4
    print(f"found {len(magics)} DTB candidate(s)")
    for n, (o, s, tag) in enumerate(magics):
        end = (
            s
            if s
            else (
                magics[n + 1][1]
                if n + 1 < len(magics) and magics[n + 1][0]
                else len(dtb_blob)
            )
        )
        if s is None:
            # raw mode: next magic is the end; scan backwards from next magic for FDT terminator not reliable,
            # use total size when possible; else to end of file
            nxt = magics[n + 1][0] if n + 1 < len(magics) else len(dtb_blob)
            end = nxt
        blob = dtb_blob[o:end]
        # DTB total size is at offset 4 (big endian)
        if len(blob) >= 8 and blob[0:4] == b"\xd0\x0d\xfe\xed":
            total = struct.unpack_from(">I", blob, 4)[0]
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
