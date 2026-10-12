// uefi.hpp
#pragma once

#include "types.hpp"

namespace cpp_uefi {

// Learning-only placeholders. These are not a complete or ABI-compatible
// replacement for the official UEFI specification headers.
enum class Status : Uintn {
    Success = 0,
    InvalidParameter = static_cast<Uintn>(0x8000000000000002ULL),
    Unsupported = static_cast<Uintn>(0x8000000000000003ULL),
};

struct Guid {
    Uint32 data1;
    Uint16 data2;
    Uint16 data3;
    Uint8 data4[8];
};

} // namespace cpp_uefi
