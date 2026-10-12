# efi_parser.py
"""Top-level read-only file recognizer for EFI-related binaries and payloads."""

from pathlib import Path

from .pe_parser import parse_pe
from .firmware_volume import inspect_firmware_volume
from .mach_o_parser import parse_mach_o


def inspect_file(source):
    """Inspect one file and return a Python dictionary of findings."""
    path = Path(source) if not isinstance(source, (bytes, bytearray, memoryview)) else None
    data = bytes(source) if path is None else path.read_bytes()
    suffix = path.suffix.lower() if path else ""

    result = {
        "filename": path.name if path else "<bytes>",
        "path": str(path) if path else None,
        "extension": suffix,
        "size_bytes": len(data),
    }

    pe = parse_pe(data)
    if pe.get("is_pe"):
        result["detected_format"] = "PE/COFF"
        result["pe"] = pe
    else:
        mach = parse_mach_o(data)
        if mach.get("is_mach_o"):
            result["detected_format"] = "Mach-O"
            result["mach_o"] = mach
        elif data.startswith(b"IM4P"):
            result["detected_format"] = "IM4P payload (signature heuristic)"
        elif data.startswith(b"IMG4"):
            result["detected_format"] = "IMG4 container (signature heuristic)"
        elif data.startswith(b"bvx2"):
            result["detected_format"] = "Possible LZFSE-compressed data"
        else:
            result["detected_format"] = "Unknown or wrapped binary"

    if suffix in {".fd", ".rom", ".bin", ".scap", ".im4p", ".img4"} or result["detected_format"] == "Unknown or wrapped binary":
        result["firmware_volume_scan"] = inspect_firmware_volume(data)

    return result
