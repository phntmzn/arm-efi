# inspect_firmware.py
"""Command-line, read-only firmware inspector. Prints results to the terminal."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from arm_uefi.efi_parser import inspect_file

DEFAULT_ROOTS = [
    "/usr/standalone/firmware/FUD",
    "/usr/standalone/i386",
    "/System/Volumes/Preboot",
]
EXTENSIONS = {".efi", ".im4p", ".img4", ".scap", ".fd", ".rom", ".bin"}


def discover(paths, all_files=False, efi_only=False):
    found, seen = [], set()
    for raw in paths:
        root = Path(raw).expanduser()
        if not root.exists():
            print(f"[SKIP] Not found: {root}", file=sys.stderr)
            continue
        print(f"[SCAN] {root}", file=sys.stderr)
        try:
            candidates = [root] if root.is_file() else root.rglob("*")
            for path in candidates:
                try:
                    if not path.is_file():
                        continue
                    if efi_only and path.suffix.lower() != ".efi":
                        continue
                    if not all_files and not efi_only and path.suffix.lower() not in EXTENSIONS:
                        continue
                    resolved = str(path.resolve())
                    if resolved not in seen:
                        seen.add(resolved)
                        found.append(path)
                except OSError:
                    continue
        except OSError as exc:
            print(f"[SKIP] Cannot scan {root}: {exc}", file=sys.stderr)
    return found


def main():
    parser = argparse.ArgumentParser(description="Inspect EFI and firmware files without executing or modifying them.")
    parser.add_argument("paths", nargs="*", help="Optional file(s) or directory/directories.")
    parser.add_argument("--efi-only", action="store_true", help="Inspect only .efi files.")
    parser.add_argument("--all-files", action="store_true", help="Inspect all files in selected directories.")
    args = parser.parse_args()

    paths = args.paths or DEFAULT_ROOTS
    files = discover(paths, all_files=args.all_files, efi_only=args.efi_only)
    print(f"\nFound {len(files)} candidate file(s).\n")

    for index, path in enumerate(files, 1):
        try:
            result = inspect_file(path)
            print(f"[{index}/{len(files)}] {path}")
            print(f"  Format: {result.get('detected_format', 'Unknown')}")
            print(f"  Size: {result.get('size_bytes', 0):,} bytes")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            print(f"  SHA-256: {digest}")

            pe = result.get("pe", {})
            if pe:
                print(f"  Architecture: {pe.get('architecture', 'Unknown')}")
                print(f"  Subsystem: {pe.get('subsystem', 'Unknown')}")
                print(f"  Sections: {pe.get('section_count', 0)}")
                for section in pe.get("sections", []):
                    print(
                        f"    {section['name']}: RVA=0x{section['virtual_address']:x}, "
                        f"file offset=0x{section['raw_offset']:x}, raw size={section['raw_size']}"
                    )

            mach = result.get("mach_o", {})
            if mach:
                print(f"  Architecture: {mach.get('architecture', 'Unknown')}")
                print(f"  Byte order: {mach.get('byte_order', 'Unknown')}")

            fv = result.get("firmware_volume_scan", {})
            if fv:
                print(f"  FV signatures: {fv.get('signature_count', 0)}")
                for match in fv.get("matches", []):
                    print(
                        f"    offset=0x{match['signature_offset']:x}, "
                        f"plausible={match['plausible_header']}"
                    )
            print()
        except (OSError, ValueError, struct.error) as exc:
            print(f"[ERROR] {path}: {exc}\n", file=sys.stderr)

    print(f"Files inspected: {len(files)}")


if __name__ == "__main__":
    import struct
    main()
