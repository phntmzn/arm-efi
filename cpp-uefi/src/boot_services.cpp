// boot_services.cpp
#include "boot_services.hpp"

namespace cpp_uefi {
Status BootServices::available() const noexcept {
    // Host-side scaffold: real UEFI boot services are not available in macOS.
    return Status::Unsupported;
}
}
