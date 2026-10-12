; startup.asm
; Educational placeholder only. EDK II normally supplies the UEFI application
; entry point and architecture-specific startup/ABI handling.
; This file is not used by the host-side Makefile.
bits 64
section .text
global cpp_uefi_startup_placeholder
cpp_uefi_startup_placeholder:
    ret
