// window.cpp - SDL2 window implementation for Platyplaty renderer

#include "window.hpp"
#include <SDL_opengl.h>
#include <stdexcept>
#include <string>

namespace platyplaty {

namespace {

constexpr int INITIAL_WIDTH = 1280;
constexpr int INITIAL_HEIGHT = 720;
constexpr char const* WINDOW_TITLE = "Platyplaty";

void set_gl_attributes() {
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 2);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,
                        SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
}

void enable_vsync() {
    // Try adaptive vsync first, fall back to regular vsync
    if (SDL_GL_SetSwapInterval(-1) != 0) {
        SDL_GL_SetSwapInterval(1);
    }
}

} // anonymous namespace

Window::Window() {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        throw std::runtime_error(
            std::string("SDL_Init failed: ") + SDL_GetError());
    }
    m_sdl_initialized = true;

    set_gl_attributes();

    constexpr Uint32 flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE |
                             SDL_WINDOW_ALLOW_HIGHDPI | SDL_WINDOW_HIDDEN;

    m_window = SDL_CreateWindow(WINDOW_TITLE, SDL_WINDOWPOS_CENTERED,
                               SDL_WINDOWPOS_CENTERED, INITIAL_WIDTH,
                               INITIAL_HEIGHT, flags);
    if (m_window == nullptr) {
        throw std::runtime_error(
            std::string("SDL_CreateWindow failed: ") + SDL_GetError());
    }

    m_gl_context = SDL_GL_CreateContext(m_window);
    if (m_gl_context == nullptr) {
        throw std::runtime_error(
            std::string("SDL_GL_CreateContext failed: ") + SDL_GetError());
    }

    enable_vsync();
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
}

Window::~Window() {
    if (m_gl_context != nullptr) {
        SDL_GL_DeleteContext(m_gl_context);
    }
    if (m_window != nullptr) {
        SDL_DestroyWindow(m_window);
    }
    if (m_sdl_initialized) {
        SDL_Quit();
    }
}

std::pair<int, int> Window::get_drawable_size() const {
    int width = 0;
    int height = 0;
    SDL_GL_GetDrawableSize(m_window, &width, &height);
    return {width, height};
}

void Window::swap_buffers() {
    SDL_GL_SwapWindow(m_window);
}

void Window::show() {
    SDL_ShowWindow(m_window);
    m_visible = true;
}

void Window::set_fullscreen(bool enabled) {
    Uint32 flag = enabled ? SDL_WINDOW_FULLSCREEN_DESKTOP : 0;
    SDL_SetWindowFullscreen(m_window, flag);
}

} // namespace platyplaty
