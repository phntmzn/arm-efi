# pe_parser.py
"""Minimal, read-only PE/COFF metadata parser using only the Python standard library."""

from pathlib import Path
import struct


MACHINE_TYPES = {
    0x014C: "x86",
    0x01C0: "ARM",
    0x01C2: "ARM Thumb-2",
    0x8664: "x86-64",
    0xAA64: "ARM64 / AArch64",
}

SUBSYSTEMS = {
    1: "Native",
    2: "Windows GUI",
    3: "Windows console",
    10: "EFI application",
    11: "EFI boot-service driver",
    12: "EFI runtime driver",
    13: "EFI ROM",
    16: "Windows boot application",
}


def parse_pe(source):
    """Parse PE metadata from a path or bytes-like object; never executes the file."""
    data = _read_bytes(source)
    result = {"format": "unknown", "is_pe": False, "size_bytes": len(data)}

    if len(data) < 64 or data[:2] != b"MZ":
        result["error"] = "Missing or incomplete DOS MZ header"
        return result

    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if pe_offset < 64 or pe_offset + 24 > len(data):
        result["error"] = "PE header offset is outside the file"
        return result
    if data[pe_offset:pe_offset + 4] != b"PE\x00\x00":
        result["error"] = "PE signature not found"
        return result

    coff_offset = pe_offset + 4
    machine, sections, timestamp, sym_ptr, sym_count, opt_size, characteristics = (
        struct.unpack_from("<HHIIIHH", data, coff_offset)
    )
    opt_offset = coff_offset + 20
    opt_end = opt_offset + opt_size
    if opt_end > len(data):
        result["error"] = "Optional header extends beyond file"
        return result

    optional = data[opt_offset:opt_end]
    magic = struct.unpack_from("<H", optional, 0)[0] if len(optional) >= 2 else None
    subsystem = struct.unpack_from("<H", optional, 68)[0] if len(optional) >= 70 else None

    section_table = opt_end
    section_rows = []
    for index in range(sections):
        offset = section_table + index * 40
        if offset + 40 > len(data):
            break
        row = data[offset:offset + 40]
        name = row[:8].split(b"\x00", 1)[0].decode("ascii", errors="replace")
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", row, 8)
        section_rows.append({
            "name": name,
            "virtual_size": virtual_size,
            "virtual_address": virtual_address,
            "raw_size": raw_size,
            "raw_offset": raw_offset,
            "raw_data_in_bounds": raw_offset + raw_size <= len(data),
        })

    result.update({
        "format": "PE/COFF",
        "is_pe": True,
        "machine": f"0x{machine:04x}",
        "architecture": MACHINE_TYPES.get(machine, "Unknown architecture"),
        "section_count": sections,
        "timestamp": timestamp,
        "characteristics": f"0x{characteristics:04x}",
        "optional_header": {0x10B: "PE32", 0x20B: "PE32+"}.get(magic, "Unknown"),
        "subsystem_id": subsystem,
        "subsystem": SUBSYSTEMS.get(subsystem, "Other or unknown") if subsystem is not None else None,
        "sections": section_rows,
    })
    return result


def _read_bytes(source):
    if isinstance(source, (bytes, bytearray, memoryview)):
        return bytes(source)
    return Path(source).read_bytes()
