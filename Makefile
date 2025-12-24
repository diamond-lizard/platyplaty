# Platyplaty Renderer Makefile
# Stage 1: Minimal proof-of-concept renderer

CXX := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -Wpedantic

# pkg-config path for non-standard libprojectM location
export PKG_CONFIG_PATH := /usr/local/apps/libprojectm/lib64/pkgconfig:$(PKG_CONFIG_PATH)

# Get flags from pkg-config
PROJECTM_CFLAGS := $(shell pkg-config --cflags projectM-4)
PROJECTM_LIBS := $(shell pkg-config --libs projectM-4)
SDL2_CFLAGS := $(shell pkg-config --cflags sdl2)
SDL2_LIBS := $(shell pkg-config --libs sdl2)

CFLAGS := $(CXXFLAGS) $(PROJECTM_CFLAGS) $(SDL2_CFLAGS)
LDFLAGS := $(PROJECTM_LIBS) $(SDL2_LIBS)

# Directories
SRC_DIR := renderer
BUILD_DIR := build

# Source files
SOURCES := $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS := $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(SOURCES))

# Target binary
TARGET := $(BUILD_DIR)/platyplaty-renderer

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@ $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
