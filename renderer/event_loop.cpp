// event_loop.cpp - Main render loop implementation for Platyplaty

#include "event_loop.hpp"
#include "shutdown.hpp"
#include "visualizer.hpp"
#include "window.hpp"
#include "command_slot.hpp"
#include "command_handler.hpp"
#include <SDL.h>
#include <SDL_opengl.h>

namespace platyplaty {

namespace {

void handle_window_event(
    const SDL_Event& event,
    const Window& window,
    Visualizer& visualizer) {
    if (event.window.event == SDL_WINDOWEVENT_SIZE_CHANGED) {
        auto [width, height] = window.get_drawable_size();
        visualizer.set_window_size(width, height);
    }
}

void process_events(const Window& window, Visualizer& visualizer) {
    SDL_Event event;
    while (SDL_PollEvent(&event) != 0) {
        if (event.type == SDL_QUIT) {
            g_shutdown_requested.store(true, std::memory_order_relaxed);
        } else if (event.type == SDL_WINDOWEVENT) {
            handle_window_event(event, window, visualizer);
        }
    }
}

void render_frame(Window& window, Visualizer& visualizer) {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    visualizer.render_frame();
    window.swap_buffers();
}

} // anonymous namespace

void run_event_loop(Window& window, Visualizer& visualizer, CommandSlot& command_slot) {
    bool running = true;
    while (running && !g_shutdown_requested.load(std::memory_order_relaxed)) {
        process_events(window, visualizer);

        // Process any pending command from socket thread
        if (auto cmd_opt = command_slot.try_get_command()) {
            auto resp = handle_command(*cmd_opt, visualizer, window, running);
            command_slot.put_response(resp);
        }
        render_frame(window, visualizer);
    }
}

} // namespace platyplaty
