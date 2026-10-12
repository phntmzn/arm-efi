// main.cpp
#include "boot_services.hpp"
#include "console.hpp"
#include "memory.hpp"

#include <iostream>

int main() {
    cpp_uefi::console_write("cpp-uefi: C++ UEFI learning scaffold\n");
    cpp_uefi::console_write("This is a macOS host executable, not an EFI application.\n");

    const auto pages = cpp_uefi::pages_for_bytes(8192);
    std::cout << "Pages needed for 8192 bytes: " << pages << '\n';

    cpp_uefi::BootServices services;
    std::cout << "Boot-services facade status: "
              << static_cast<unsigned long long>(services.available())
              << '\n';
    return 0;
}
