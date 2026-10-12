# Makefile
CXX ?= clang++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Wpedantic -Iinclude
BUILD_DIR := build
SOURCES := src/main.cpp src/console.cpp src/memory.cpp src/boot_services.cpp
OBJECTS := $(SOURCES:src/%.cpp=$(BUILD_DIR)/%.o)
TARGET := $(BUILD_DIR)/cpp-uefi
TEST_TARGET := $(BUILD_DIR)/test_types

.PHONY: all clean test

all: $(TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o: src/%.cpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $@

$(TEST_TARGET): tests/test_types.cpp include/types.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) tests/test_types.cpp src/memory.cpp -o $@

test: $(TEST_TARGET)
	./$(TEST_TARGET)

clean:
	rm -rf $(BUILD_DIR)
