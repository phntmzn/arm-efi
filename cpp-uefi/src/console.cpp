// console.cpp
#include "console.hpp"

#include <iostream>

namespace cpp_uefi {
void console_write(std::string_view text) {
    std::cout << text;
}
}
