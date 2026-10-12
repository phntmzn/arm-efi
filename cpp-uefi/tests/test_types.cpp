// test_types.cpp
#include "memory.hpp"
#include "types.hpp"

#include <cassert>
#include <cstdint>
#include <limits>

int main() {
    using cpp_uefi::pages_for_bytes;
    using cpp_uefi::kPageSize;

    static_assert(sizeof(cpp_uefi::Uint8) == 1);
    static_assert(sizeof(cpp_uefi::Uint16) == 2);
    static_assert(sizeof(cpp_uefi::Uint32) == 4);
    static_assert(sizeof(cpp_uefi::Uint64) == 8);

    assert(pages_for_bytes(0) == 0);
    assert(pages_for_bytes(1) == 1);
    assert(pages_for_bytes(kPageSize) == 1);
    assert(pages_for_bytes(kPageSize + 1) == 2);
    assert(pages_for_bytes(8192) == 2);
    assert(pages_for_bytes(std::numeric_limits<std::uint64_t>::max()) == 0);
    return 0;
}
