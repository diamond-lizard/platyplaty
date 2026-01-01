// event_loop.cpp - Main render loop implementation for Platyplaty

#include "event_loop.hpp"
#include "shutdown.hpp"
#include "visualizer.hpp"
#include "window.hpp"
#include "command_slot.hpp"
#include "command_handler.hpp"
#include "key_event.hpp"
#include "scancode_map.hpp"
#include "stderr_event.hpp"
#include <SDL.h>
#include <SDL_opengl.h>

namespace platyplaty {

namespace {

// Static rate limiter for key repeat events.
KeyRateLimiter g_key_rate_limiter;

void handle_window_event(
    const SDL_Event& event,
    const Window& window,
    Visualizer& visualizer) {
    if (event.window.event == SDL_WINDOWEVENT_SIZE_CHANGED) {
        auto [width, height] = window.get_drawable_size();
        visualizer.set_window_size(width, height);
    }
}

void handle_key_event(const SDL_Event& event) {
    // Extract modifier state from keyboard state.
    const auto* state = SDL_GetKeyboardState(nullptr);
    bool ctrl = state[SDL_SCANCODE_LCTRL] || state[SDL_SCANCODE_RCTRL];
    bool shift = state[SDL_SCANCODE_LSHIFT] || state[SDL_SCANCODE_RSHIFT];
    bool alt = state[SDL_SCANCODE_LALT] || state[SDL_SCANCODE_RALT];

    // Translate scancode to key name.
    auto key_name = scancode_to_keyname(event.key.keysym.scancode, ctrl, shift, alt);
    if (!key_name) {
        return;  // Unmapped scancode.
    }

    // Check rate limiting.
    bool is_repeat = (event.key.repeat != 0);
    if (!g_key_rate_limiter.should_emit(*key_name, is_repeat)) {
        return;  // Rate-limited.
    }

    // Emit KEY_PRESSED event to stderr.
    emit_key_pressed(*key_name);
}

void process_events(const Window& window, Visualizer& visualizer) {
    SDL_Event event;
    while (SDL_PollEvent(&event) != 0) {
        if (event.type == SDL_QUIT) {
            g_shutdown_requested.store(true, std::memory_order_relaxed);
        } else if (event.type == SDL_WINDOWEVENT) {
            handle_window_event(event, window, visualizer);
        } else if (event.type == SDL_KEYDOWN) {
            handle_key_event(event);
        }
    }
}

void render_frame(Window& window, Visualizer& visualizer) {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    visualizer.render_frame();
    window.swap_buffers();
}

} // anonymous namespace

void run_event_loop(Window& window, Visualizer& visualizer, CommandSlot& command_slot, const AudioCapture& audio) {
    bool running = true;
    while (running && !g_shutdown_requested.load(std::memory_order_relaxed)) {
        process_events(window, visualizer);

        // Process any pending command from socket thread
        if (auto cmd_opt = command_slot.try_get_command()) {
            auto resp = handle_command(*cmd_opt, visualizer, window, running, audio);
            command_slot.put_response(resp);
        }
        render_frame(window, visualizer);
    }
}

} // namespace platyplaty
