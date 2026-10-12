# firmware_volume.py
"""Read-only heuristic detection for UEFI PI firmware-volume headers."""

from pathlib import Path
import struct

# EFI_FIRMWARE_VOLUME_HEADER.FvSignature is the ASCII byte sequence "_FVH"
FV_SIGNATURE = b"_FVH"


def inspect_firmware_volume(source):
    """Search for an FV signature and validate basic header fields heuristically.

    This is a lightweight signature scanner, not a complete PI/UEFI parser.
    """
    data = _read_bytes(source)
    matches = []
    start = 0

    while True:
        offset = data.find(FV_SIGNATURE, start)
        if offset < 0:
            break
        start = offset + 1

        # FvSignature is 40 bytes into a standard EFI_FIRMWARE_VOLUME_HEADER.
        header_offset = offset - 40
        if header_offset < 0 or header_offset + 56 > len(data):
            matches.append({
                "signature_offset": offset,
                "header_offset": header_offset,
                "plausible_header": False,
                "note": "Signature found, but a complete standard header is unavailable",
            })
            continue

        fv_length = struct.unpack_from("<Q", data, header_offset + 32)[0]
        attributes = struct.unpack_from("<I", data, header_offset + 44)[0]
        header_length = struct.unpack_from("<H", data, header_offset + 48)[0]
        checksum = struct.unpack_from("<H", data, header_offset + 50)[0]
        revision = data[header_offset + 55]

        plausible = (
            56 <= header_length <= 4096
            and fv_length >= header_length
            and header_offset + fv_length <= len(data)
        )
        matches.append({
            "signature_offset": offset,
            "header_offset": header_offset,
            "firmware_volume_length": fv_length,
            "attributes": f"0x{attributes:08x}",
            "header_length": header_length,
            "checksum": f"0x{checksum:04x}",
            "revision": revision,
            "plausible_header": plausible,
        })

    return {
        "format": "firmware-volume signature scan",
        "size_bytes": len(data),
        "signature_count": len(matches),
        "matches": matches,
    }


def _read_bytes(source):
    if isinstance(source, (bytes, bytearray, memoryview)):
        return bytes(source)
    return Path(source).read_bytes()
