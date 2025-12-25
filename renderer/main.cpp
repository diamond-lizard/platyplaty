// main.cpp - Entry point for Platyplaty renderer
// Stage 1: Minimal proof-of-concept with SDL2 window and projectM.

#include "shutdown.hpp"
#include "event_loop.hpp"
#include "visualizer.hpp"
#include "window.hpp"
#include <cstdlib>
#include <iostream>

namespace {
constexpr char const* PRESET_PATH = "presets/test/101-per_frame.milk";
} // anonymous namespace

// cppcheck-suppress unusedFunction ; SDL_main macro redefinition
int main() {
    platyplaty::setup_signal_handlers();

    try {
        platyplaty::Window window;
        auto [width, height] = window.get_drawable_size();
        platyplaty::Visualizer visualizer(width, height);

        auto result = visualizer.load_preset(PRESET_PATH);
        if (!result.success) {
            std::cerr << "Warning: Failed to load preset: " << result.error_message << '\n';
        }

        platyplaty::run_event_loop(window, visualizer);
        return EXIT_SUCCESS;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
}
