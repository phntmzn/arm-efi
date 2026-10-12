# test_efi_parser.py
"""Small unit tests for the read-only parsers."""

import struct
import unittest

from arm_uefi.efi_parser import inspect_file
from arm_uefi.pe_parser import parse_pe
from arm_uefi.mach_o_parser import parse_mach_o
from arm_uefi.firmware_volume import inspect_firmware_volume


def make_minimal_pe(machine=0xAA64, subsystem=10):
    """Create a small synthetic PE image for parser tests."""
    data = bytearray(0x200)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", data, 0x84, machine, 0, 0, 0, 0, 0x70, 0x0002)
    optional = 0x84 + 20
    struct.pack_into("<H", data, optional, 0x20B)
    struct.pack_into("<H", data, optional + 68, subsystem)
    return bytes(data)


class ParserTests(unittest.TestCase):
    def test_parse_arm64_efi_pe(self):
        result = parse_pe(make_minimal_pe())
        self.assertTrue(result["is_pe"])
        self.assertEqual(result["architecture"], "ARM64 / AArch64")
        self.assertEqual(result["subsystem"], "EFI application")

    def test_reject_non_pe(self):
        result = parse_pe(b"not a PE file")
        self.assertFalse(result["is_pe"])

    def test_reject_non_macho(self):
        result = parse_mach_o(b"not Mach-O")
        self.assertFalse(result["is_mach_o"])

    def test_firmware_volume_without_signature(self):
        result = inspect_firmware_volume(b"no firmware volume here")
        self.assertEqual(result["signature_count"], 0)

    def test_inspect_bytes(self):
        result = inspect_file(make_minimal_pe())
        self.assertEqual(result["detected_format"], "PE/COFF")


if __name__ == "__main__":
    unittest.main()
