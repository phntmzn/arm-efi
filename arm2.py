# analyze_firmware.py

import argparse
import hashlib
import struct
from pathlib import Path


MACHINE_TYPES = {
    0xAA64: "ARM64 / AArch64",
    0x8664: "x86-64",
    0x014C: "x86",
    0x01C0: "ARM",
    0x01C2: "ARM Thumb-2",
}

KNOWN_EXTENSIONS = {
    ".efi",
    ".im4p",
    ".img4",
    ".scap",
    ".fd",
    ".rom",
}

DEFAULT_ROOTS = [
    "/usr/standalone/firmware/FUD",
    "/usr/standalone/i386",
    "/System/Volumes/Preboot",
]


def sha256_file(path):
    """Calculate a file's SHA-256 hash."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def identify_pe(path, size):
    """Extract PE/COFF metadata without executing the file."""

    result = {}

    with path.open("rb") as file:
        file.seek(0x3C)
        raw_offset = file.read(4)

        if len(raw_offset) != 4:
            raise ValueError("Incomplete DOS header")

        pe_offset = struct.unpack("<I", raw_offset)[0]

        if pe_offset < 64 or pe_offset > size - 24:
            raise ValueError("Invalid PE header offset")

        file.seek(pe_offset)

        if file.read(4) != b"PE\x00\x00":
            raise ValueError("PE signature not found")

        coff_header = file.read(20)

        if len(coff_header) != 20:
            raise ValueError("Incomplete COFF header")

        (
            machine,
            sections,
            timestamp,
            symbol_table,
            symbol_count,
            optional_size,
            characteristics,
        ) = struct.unpack("<HHIIIHH", coff_header)

        result.update({
            "format": "PE/COFF",
            "machine": hex(machine),
            "architecture": MACHINE_TYPES.get(
                machine, "Unknown architecture"
            ),
            "section_count": sections,
            "characteristics": hex(characteristics),
            "coff_timestamp": timestamp,
        })

        optional_header = file.read(optional_size)

        if len(optional_header) < 2:
            raise ValueError("Missing PE optional header")

        magic = struct.unpack_from("<H", optional_header)[0]

        result["optional_header"] = {
            0x10B: "PE32",
            0x20B: "PE32+",
        }.get(magic, "Unknown")

        if len(optional_header) >= 70:
            subsystem = struct.unpack_from(
                "<H", optional_header, 68
            )[0]

            result["subsystem_id"] = subsystem
            result["subsystem"] = {
                10: "EFI application",
                11: "EFI boot-service driver",
                12: "EFI runtime driver",
                13: "EFI ROM",
                16: "Windows boot application",
            }.get(subsystem, "Other or unknown subsystem")

    return result


def identify_format(header):
    """Identify common executable and firmware signatures."""

    if header.startswith(b"MZ"):
        return "DOS/PE candidate"

    if header.startswith(b"IMG4"):
        return "IMG4 container signature"

    if header.startswith(b"IM4P"):
        return "IM4P payload signature"

    if header.startswith(b"Joy!"):
        return "Possible Apple firmware payload"

    if header.startswith(b"VZ"):
        return "Possible compressed or custom payload"

    if header.startswith(b"\x7fELF"):
        return "ELF executable"

    if header.startswith(b"\xcf\xfa\xed\xfe"):
        return "Mach-O 64-bit executable (little-endian)"

    if header.startswith(b"\xfe\xed\xfa\xcf"):
        return "Mach-O 64-bit executable (big-endian)"

    if header.startswith(b"bvx2"):
        return "Possible LZFSE-compressed data"

    return "Unknown binary format"


def inspect_file(path):
    """Inspect a firmware-related file without executing or modifying it."""

    result = {
        "path": str(path),
        "filename": path.name,
        "extension": path.suffix.lower(),
    }

    try:
        result["size_bytes"] = path.stat().st_size

        with path.open("rb") as file:
            header = file.read(4096)

        result["sha256"] = sha256_file(path)
        result["format"] = identify_format(header)

        if result["format"] == "DOS/PE candidate":
            try:
                result.update(
                    identify_pe(path, result["size_bytes"])
                )
            except (OSError, ValueError, struct.error) as exc:
                result["header_analysis_error"] = str(exc)

        elif result["format"] == "ELF executable":
            if len(header) >= 20 and header[5] in (1, 2):
                endian = "<" if header[5] == 1 else ">"
                machine = struct.unpack_from(
                    endian + "H", header, 18
                )[0]

                result["machine"] = hex(machine)
                result["architecture"] = {
                    183: "AArch64",
                    62: "x86-64",
                    3: "x86",
                }.get(machine, "Unknown architecture")

        extension = path.suffix.lower()

        result["artifact_category"] = {
            ".im4p": "Apple firmware payload",
            ".img4": "Apple firmware container",
            ".scap": "Firmware capsule",
            ".efi": "EFI candidate",
            ".fd": "Firmware image candidate",
            ".rom": "ROM image candidate",
        }.get(extension, "Other firmware-related file")

    except OSError as exc:
        result["error"] = str(exc)

    return result


def discover_files(roots, extensions=None):
    """Find matching files recursively while skipping inaccessible paths."""

    found = []
    seen = set()

    for root in roots:
        root = Path(root).expanduser()

        if not root.exists():
            print(f"[SKIP] Not found: {root}")
            continue

        if not root.is_dir() and not root.is_file():
            continue

        print(f"[SCAN] {root}")

        try:
            candidates = [root] if root.is_file() else root.rglob("*")

            for path in candidates:
                try:
                    if not path.is_file():
                        continue

                    if (
                        extensions is not None
                        and path.suffix.lower() not in extensions
                    ):
                        continue

                    resolved = str(path.resolve())

                    if resolved in seen:
                        continue

                    seen.add(resolved)
                    found.append(path)

                except (OSError, PermissionError):
                    continue

        except (OSError, PermissionError) as exc:
            print(f"[SKIP] Cannot scan {root}: {exc}")

    return found


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Inventory macOS firmware files and inspect "
            "EFI/PE executable metadata."
        )
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional files or directories to inspect.",
    )

    parser.add_argument(
        "--efi-only",
        action="store_true",
        help="Inspect only files with the .efi extension.",
    )

    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Inspect all files in the selected directories.",
    )

    args = parser.parse_args()

    roots = args.paths or DEFAULT_ROOTS

    if args.efi_only:
        extensions = {".efi"}
    elif args.all_files:
        extensions = None
    else:
        extensions = KNOWN_EXTENSIONS

    files = discover_files(roots, extensions)

    print(f"\nFound {len(files)} candidate files.\n")

    results = []

    for index, path in enumerate(files, start=1):
        result = inspect_file(path)
        results.append(result)

        print(f"[{index}/{len(files)}] {path}")
        print(f"  Format: {result.get('format', 'Unknown')}")

        if "architecture" in result:
            print(f"  Architecture: {result['architecture']}")

        if "subsystem" in result:
            print(f"  Subsystem: {result['subsystem']}")

        if "size_bytes" in result:
            print(f"  Size: {result['size_bytes']:,} bytes")

        if "error" in result:
            print(f"  Error: {result['error']}")

    print(f"\nFiles analyzed: {len(results)}")


if __name__ == "__main__":
    main()