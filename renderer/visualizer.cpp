// visualizer.cpp - ProjectM visualization implementation for Platyplaty

#include "visualizer.hpp"
#include <cstring>
#include <fstream>
#include <stdexcept>

namespace platyplaty {

Visualizer::Visualizer(std::size_t width, std::size_t height)
    : m_handle(create_projectm_instance()),
      m_width(width),
      m_height(height) {

    projectm_set_window_size(m_handle, width, height);
    projectm_set_preset_locked(m_handle, true);

    projectm_set_preset_switch_failed_event_callback(
        m_handle, preset_switch_failed_callback, this);
}

Visualizer::~Visualizer() {
    if (m_handle != nullptr) {
        projectm_destroy(m_handle);
    }
}

void Visualizer::set_window_size(std::size_t width, std::size_t height) {
    if (width == m_width && height == m_height) {
        return;
    }
    m_width = width;
    m_height = height;
    projectm_set_window_size(m_handle, width, height);
}

void Visualizer::render_frame() {
    projectm_opengl_render_frame(m_handle);
}

PresetLoadResult Visualizer::load_preset(const std::string& path, bool smooth_transition) {
    // Clear error buffer before attempting load
    m_error_buffer[0] = '\0';

    // Handle idle:// URL - skip file validation
    if (path == "idle://") {
        m_current_preset_path = path;
        return {true, ""};
    }

    // Check if file exists and is readable
    std::ifstream file(path);
    if (!file.good()) {
        return {false, "file not found: " + path};
    }
    file.close();

    // Attempt to load the preset with smooth transition
    projectm_load_preset_file(m_handle, path.c_str(), smooth_transition);

    // Check if callback captured an error
    if (m_error_buffer[0] != '\0') {
        return {false, std::string(m_error_buffer)};
    }

    m_current_preset_path = path;
    return {true, ""};
}

void Visualizer::preset_switch_failed_callback(
        const char* preset_filename,
        const char* message,
        void* user_data) {
    auto* self = static_cast<Visualizer*>(user_data);
    std::strncpy(self->m_error_buffer, message, ERROR_BUFFER_SIZE - 1);
    self->m_error_buffer[ERROR_BUFFER_SIZE - 1] = '\0';
    (void)preset_filename; // Unused parameter
}

projectm_handle Visualizer::create_projectm_instance() {
    projectm_handle handle = projectm_create();
    if (handle == nullptr) {
        throw std::runtime_error("Failed to create projectM instance");
    }
    return handle;
}

const std::string& Visualizer::get_current_preset_path() const {
    return m_current_preset_path;
}

} // namespace platyplaty
