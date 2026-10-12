// types.hpp
#pragma once

#include <cstddef>
#include <cstdint>

namespace cpp_uefi {
using Boolean = std::uint8_t;
using Uint8 = std::uint8_t;
using Uint16 = std::uint16_t;
using Uint32 = std::uint32_t;
using Uint64 = std::uint64_t;
using Intn = std::intptr_t;
using Uintn = std::uintptr_t;

constexpr Uint64 kPageSize = 4096;
}
