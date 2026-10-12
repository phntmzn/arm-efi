/* uefi.ld
 * Educational placeholder. Do not use this script to link a production EFI
 * application. Use the linker/build settings provided by a compatible EDK II
 * toolchain and target platform.
 */
SECTIONS
{
    .text : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data : { *(.data*) }
    .bss : { *(.bss*) }
}
