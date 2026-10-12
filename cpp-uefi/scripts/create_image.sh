#!/bin/sh
# create_image.sh
set -eu

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <UEFI-application.efi> <output-image.img>" >&2
    exit 2
fi

EFI_APP=$1
OUTPUT=$2

if [ ! -f "$EFI_APP" ]; then
    echo "Error: EFI application not found: $EFI_APP" >&2
    exit 1
fi

case "$OUTPUT" in
    /dev/*) echo "Refusing to write to a device path: $OUTPUT" >&2; exit 1 ;;
esac

if ! command -v mformat >/dev/null 2>&1 || ! command -v mcopy >/dev/null 2>&1; then
    echo "Missing mtools. Install with: brew install mtools" >&2
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT HUP INT TERM

# Create a 64 MiB image file, then format it as FAT.
dd if=/dev/zero of="$OUTPUT" bs=1m count=64
mformat -i "$OUTPUT" -F ::
mkdir -p "$TMP_DIR/EFI/BOOT"
case "$(uname -m)" in
    arm64) BOOT_NAME=BOOTAA64.EFI ;;
    *) BOOT_NAME=BOOTX64.EFI ;;
esac
cp "$EFI_APP" "$TMP_DIR/EFI/BOOT/$BOOT_NAME"
mcopy -i "$OUTPUT" -s "$TMP_DIR/EFI" ::
echo "Created image file: $OUTPUT"
echo "Note: confirm that the EFI application architecture matches your target."
