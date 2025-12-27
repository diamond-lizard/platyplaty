# Platyplaty Renderer Makefile
# Stage 1: Minimal proof-of-concept renderer

CXX := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -Wpedantic

# Get flags from pkg-config
#
# Workaround: libprojectM 4.1.6 pkg-config file has a bug where it outputs
# "-l:projectM-4" instead of "-lprojectM-4". The "-l:" syntax tells the linker
# to find a file named exactly "projectM-4", but the library follows the
# standard naming convention "libprojectM-4.so" which requires "-lprojectM-4".
# The sed command strips the colon. If upstream fixes this bug, the sed
# command becomes a no-op and the Makefile continues to work without changes.
PROJECTM_CFLAGS := $(shell pkg-config --cflags projectM-4)
PROJECTM_LIBS := $(shell pkg-config --libs projectM-4 | sed 's/-l:/-l/g')
SDL2_CFLAGS := $(shell pkg-config --cflags sdl2)
SDL2_LIBS := $(shell pkg-config --libs sdl2)
PULSE_CFLAGS := $(shell pkg-config --cflags libpulse)
PULSE_LIBS := $(shell pkg-config --libs libpulse)

CFLAGS := $(CXXFLAGS) $(PROJECTM_CFLAGS) $(SDL2_CFLAGS) $(PULSE_CFLAGS)
LDFLAGS := $(PROJECTM_LIBS) $(SDL2_LIBS) $(PULSE_LIBS)


# Directories
SRC_DIR := renderer
BUILD_DIR := build

# Source files
SOURCES := $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS := $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(SOURCES))

# Target binary
TARGET := $(BUILD_DIR)/platyplaty-renderer

.PHONY: help renderer clean cppcheck-renderer test-renderer ruff mypy ruff-fix test

help:
	@echo "Available targets:"
	@echo "  clean             Remove build artifacts"
	@echo "  cppcheck-renderer Run cppcheck on renderer source"
	@echo "  mypy              Run mypy type checker on Python source"
	@echo "  renderer          Build the platyplaty renderer"
	@echo "  ruff              Run ruff linter on Python source"
	@echo "  ruff-fix          Auto-fix ruff issues"
	@echo "  test              Run ruff, mypy, then pytest"
	@echo "  test-renderer     Run all renderer tests"

renderer: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@ $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	find $(BUILD_DIR) -type f ! -name '.keep' -delete

cppcheck-renderer:
	cppcheck --enable=all --std=c++17 --inline-suppr --suppress=missingIncludeSystem $(SRC_DIR)

test-renderer: cppcheck-renderer
	uv run pytest tests/renderer/

ruff:
	uv run ruff check src/

mypy:
	uv run mypy src/

ruff-fix:
	uv run ruff check --fix src/

test: ruff mypy
	uv run pytest tests/
