# cpp-uefi

A starter C++ project for learning UEFI concepts on macOS. This is a **scaffold**, not a complete firmware implementation. UEFI applications run under firmware that already implements the UEFI specification.

## Project layout

```text
cpp-uefi/
├── README.md
├── Makefile
├── include/
│   ├── uefi.hpp
│   ├── types.hpp
│   ├── console.hpp
│   ├── memory.hpp
│   └── boot_services.hpp
├── src/
│   ├── main.cpp
│   ├── console.cpp
│   ├── memory.cpp
│   └── boot_services.cpp
├── boot/
│   └── startup.asm
├── linker/
│   └── uefi.ld
├── scripts/
│   └── create_image.sh
├── build/
└── tests/
    └── test_types.cpp
```

## Requirements

- macOS with Xcode Command Line Tools
- CMake or Make (the included Makefile is a small local scaffold)
- Optional for later firmware testing: QEMU and a compatible OVMF build
- For a real UEFI application build, use the [TianoCore EDK II](https://github.com/tianocore/edk2) build system and its UEFI headers/libraries. The local Makefile only compiles the host-side learning scaffold; it does **not** produce a bootable `.efi` file.

Install common tools with Homebrew:

```sh
xcode-select --install
brew install git make nasm qemu
```

## Build the host-side scaffold

```sh
make
make test
```

The default build compiles the C++ learning components as a normal macOS executable. It does not interact with or modify your Mac's firmware.

## Create an EFI image

`scripts/create_image.sh` is a guarded placeholder for the later image-building step. It requires an existing EFI application at `build/BOOTX64.EFI` and a destination path. It will not format or overwrite a disk device. The script requires `mtools` (`brew install mtools`) and creates a disk image file only.

```sh
brew install mtools
make
# Once you have built a real UEFI app with EDK II:
cp /path/to/your/UEFI/application.efi build/BOOTX64.EFI
./scripts/create_image.sh build/BOOTX64.EFI build/uefi.img
```

The host-side `build/cpp-uefi` executable is not an EFI application and cannot be used as `BOOTX64.EFI`.

## Safety

Do not flash experimental firmware onto a physical machine. Start with a virtual machine and known-compatible OVMF firmware. Apple Silicon boot firmware is platform-specific and is not replaced by this generic project.
