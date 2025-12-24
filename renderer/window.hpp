// window.hpp - SDL2 window with OpenGL context for Platyplaty renderer
// RAII class that manages SDL2 initialization, window, and OpenGL context.

#ifndef PLATYPLATY_WINDOW_HPP
#define PLATYPLATY_WINDOW_HPP

#include <SDL.h>
#include <utility>

namespace platyplaty {

// RAII wrapper for SDL2 window with OpenGL context.
// Throws std::runtime_error if initialization fails.
class Window {
public:
    // Create window with OpenGL context. Throws on failure.
    Window();

    // Non-copyable
    Window(const Window&) = delete;
    Window& operator=(const Window&) = delete;

    // Non-movable
    Window(Window&&) = delete;
    Window& operator=(Window&&) = delete;

    // Cleanup SDL resources
    ~Window();

    // Get drawable size in pixels (for HiDPI support)
    std::pair<int, int> get_drawable_size() const;

    // cppcheck-suppress unusedFunction ; Stage 2+ scaffolding for audio integration
    SDL_Window* get_sdl_window() const { return window_; }

    // Swap OpenGL buffers
    void swap_buffers();

private:
    SDL_Window* window_ = nullptr;
    SDL_GLContext gl_context_ = nullptr;
    bool sdl_initialized_ = false;
};

} // namespace platyplaty

#endif // PLATYPLATY_WINDOW_HPP
