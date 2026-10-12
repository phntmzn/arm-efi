# ARM UEFI Lab

A small, read-only Python toolkit for inspecting EFI/PE executables and selected firmware binary formats on macOS or Linux.

## Features

- Detects PE/COFF executables and reports machine architecture, EFI subsystem, and section metadata.
- Recognizes common thin Mach-O headers.
- Performs a heuristic scan for UEFI firmware-volume (`_FVH`) signatures.
- Flags common IMG4/IM4P and LZFSE signatures when they appear at the beginning of a file.
- Prints results to the terminal. It does not modify or execute firmware files.

## Requirements

- Python 3.10 or newer recommended.
- No third-party dependencies.

## Run

From the `arm-uefi-lab` directory:

```bash
python3 tools/inspect_firmware.py
```

The default scan locations are:

- `/usr/standalone/firmware/FUD`
- `/usr/standalone/i386`
- `/System/Volumes/Preboot`

Missing paths are skipped. Recursive scans of Preboot may take a while.

Inspect only `.efi` files:

```bash
python3 tools/inspect_firmware.py --efi-only
```

Inspect all files under the default roots:

```bash
python3 tools/inspect_firmware.py --all-files
```

Inspect a specific file or directory:

```bash
python3 tools/inspect_firmware.py /path/to/file.efi
python3 tools/inspect_firmware.py /path/to/firmware-directory
```

## Run tests

From the project root:

```bash
python3 -m unittest discover -s tests -v
```

## Important limitations

- File extensions and leading-byte signatures are clues, not proof of format or role.
- Apple `.im4p` payloads are not necessarily EFI executables.
- An ARM64 EFI application is not automatically compatible with Apple Silicon's native boot chain.
- The firmware-volume scan is heuristic and does not fully validate PI/UEFI structures.
- The project is read-only: it does not patch, install, sign, or execute firmware.

Use a virtual machine or dedicated test platform for experimental UEFI development. Do not experiment on your Mac's boot firmware unless you understand the platform's recovery and security model.
