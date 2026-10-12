// memory.hpp
#pragma once

#include "types.hpp"

namespace cpp_uefi {
// Round byte count up to a 4 KiB page boundary. Returns 0 on overflow.
Uint64 pages_for_bytes(Uint64 bytes) noexcept;
}
