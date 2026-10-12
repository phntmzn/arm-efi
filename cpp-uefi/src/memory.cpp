// memory.cpp
#include "memory.hpp"

#include <limits>

namespace cpp_uefi {
Uint64 pages_for_bytes(Uint64 bytes) noexcept {
    if (bytes == 0) {
        return 0;
    }
    constexpr Uint64 page_size = kPageSize;
    if (bytes > std::numeric_limits<Uint64>::max() - (page_size - 1)) {
        return 0;
    }
    return (bytes + page_size - 1) / page_size;
}
}
