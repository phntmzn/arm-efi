// boot_services.hpp
#pragma once

#include "uefi.hpp"

namespace cpp_uefi {

// Placeholder facade for learning. Actual boot services must be called
// through the System Table supplied by a UEFI firmware environment.
class BootServices {
public:
    Status available() const noexcept;
};

}
