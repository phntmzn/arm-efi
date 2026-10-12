# mach_o_parser.py
"""Read-only parser for basic Mach-O headers (not a full load-command parser)."""

from pathlib import Path
import struct

MAGIC = {
    b"\xfe\xed\xfa\xce": ("big", 32),
    b"\xce\xfa\xed\xfe": ("little", 32),
    b"\xfe\xed\xfa\xcf": ("big", 64),
    b"\xcf\xfa\xed\xfe": ("little", 64),
}
CPU_TYPES = {
    7: "x86",
    0x01000007: "x86-64",
    12: "ARM",
    0x0100000C: "ARM64 / AArch64",
}


def parse_mach_o(source):
    """Parse a thin Mach-O header from a path or bytes-like object."""
    data = _read_bytes(source)
    result = {"format": "unknown", "is_mach_o": False, "size_bytes": len(data)}

    if len(data) < 28 or data[:4] not in MAGIC:
        result["error"] = "No supported thin Mach-O magic found"
        return result

    endian_name, bits = MAGIC[data[:4]]
    endian = "<" if endian_name == "little" else ">"
    header_size = 32 if bits == 64 else 28
    if len(data) < header_size:
        result["error"] = "Incomplete Mach-O header"
        return result

    if bits == 64:
        magic, cpu, subtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack_from(
            endian + "IiiIIIII", data, 0
        )
    else:
        magic, cpu, subtype, filetype, ncmds, sizeofcmds, flags = struct.unpack_from(
            endian + "IiiIIII", data, 0
        )

    result.update({
        "format": f"Mach-O {bits}-bit",
        "is_mach_o": True,
        "byte_order": endian_name,
        "cpu_type": f"0x{cpu & 0xffffffff:08x}",
        "architecture": CPU_TYPES.get(cpu & 0xffffffff, "Unknown architecture"),
        "file_type": filetype,
        "load_command_count": ncmds,
        "load_commands_size": sizeofcmds,
        "flags": f"0x{flags:08x}",
        "header_size": header_size,
        "load_commands_in_bounds": header_size + sizeofcmds <= len(data),
    })
    return result


def _read_bytes(source):
    if isinstance(source, (bytes, bytearray, memoryview)):
        return bytes(source)
    return Path(source).read_bytes()
