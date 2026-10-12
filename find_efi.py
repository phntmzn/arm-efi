# find_efi.py

import argparse
import os
from pathlib import Path

FILE_TYPES = {
    ".efi": "EFI executable",
    ".img4": "Apple firmware container",
    ".im4p": "Apple firmware payload",
    ".scap": "Firmware capsule",
    ".fd": "Firmware image",
    ".rom": "Firmware ROM image",
}

DEFAULT_PATHS = [
    "/System/Library",
    "/System/Volumes/Preboot",
    "/usr/standalone",
    "/Volumes",
]


def find_firmware_files(roots, extensions=None):
    """
    Recursively search directories for EFI executables
    and selected firmware artifact types.

    Does not modify or execute discovered files.
    """

    if extensions is None:
        extensions = set(FILE_TYPES)

    extensions = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in extensions
    }

    results = []

    def on_error(error):
        # Continue searching when a directory is inaccessible.
        pass

    for root in roots:
        root_path = Path(root)

        if not root_path.exists():
            print(f"[SKIP] Path does not exist: {root}")
            continue

        if not root_path.is_dir():
            print(f"[SKIP] Not a directory: {root}")
            continue

        print(f"[SEARCH] {root}")

        for current, _, filenames in os.walk(
            root_path,
            onerror=on_error,
            followlinks=False,
        ):
            for filename in filenames:
                path = Path(current) / filename

                if path.suffix.lower() in extensions:
                    try:
                        size = path.stat().st_size
                    except OSError:
                        size = None

                    results.append({
                        "path": str(path),
                        "type": FILE_TYPES.get(
                            path.suffix.lower(),
                            "Unknown firmware file",
                        ),
                        "size": size,
                    })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Find EFI executables and firmware artifacts on macOS"
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="Directories to search",
    )

    parser.add_argument(
        "--efi-only",
        action="store_true",
        help="Find only files with the .efi extension",
    )

    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Search all files, not just recognized extensions",
    )

    args = parser.parse_args()

    roots = args.paths or DEFAULT_PATHS

    if args.all_files:
        extensions = None
    elif args.efi_only:
        extensions = {".efi"}
    else:
        extensions = set(FILE_TYPES)

    results = find_firmware_files(roots, extensions)

    print("\n" + "=" * 65)
    print(f"Search complete. Found {len(results)} matching files.")
    print("=" * 65)

    for item in results:
        size = (
            f"{item['size']:,} bytes"
            if item["size"] is not None
            else "size unavailable"
        )

        print(f"\nType: {item['type']}")
        print(f"Size: {size}")
        print(f"Path: {item['path']}")

    if not results:
        print(
            "\nNo matching files found. "
            "This does not mean the Mac has no firmware."
        )


if __name__ == "__main__":
    main()
