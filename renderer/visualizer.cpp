// visualizer.cpp - ProjectM visualization implementation for Platyplaty

#include "visualizer.hpp"
#include <cstring>
#include <fstream>
#include <stdexcept>

namespace platyplaty {

Visualizer::Visualizer(std::size_t width, std::size_t height)
    : handle_(create_projectm_instance()) {

    projectm_set_window_size(handle_, width, height);
    projectm_set_preset_locked(handle_, true);

    projectm_set_preset_switch_failed_event_callback(
        handle_, preset_switch_failed_callback, this);
}

Visualizer::~Visualizer() {
    if (handle_ != nullptr) {
        projectm_destroy(handle_);
    }
}

void Visualizer::set_window_size(std::size_t width, std::size_t height) {
    projectm_set_window_size(handle_, width, height);
}

void Visualizer::render_frame() {
    projectm_opengl_render_frame(handle_);
}

PresetLoadResult Visualizer::load_preset(const std::string& path) {
    // Clear error buffer before attempting load
    error_buffer_[0] = '\0';

    // Check if file exists and is readable
    std::ifstream file(path);
    if (!file.good()) {
        return {false, "file not found: " + path};
    }
    file.close();

    // Attempt to load the preset with smooth transition
    projectm_load_preset_file(handle_, path.c_str(), true);

    // Check if callback captured an error
    if (error_buffer_[0] != '\0') {
        return {false, std::string(error_buffer_)};
    }

    return {true, ""};
}

void Visualizer::preset_switch_failed_callback(
        const char* preset_filename,
        const char* message,
        void* user_data) {
    auto* self = static_cast<Visualizer*>(user_data);
    std::strncpy(self->error_buffer_, message, ERROR_BUFFER_SIZE - 1);
    self->error_buffer_[ERROR_BUFFER_SIZE - 1] = '\0';
    (void)preset_filename; // Unused parameter
}

projectm_handle Visualizer::create_projectm_instance() {
    projectm_handle handle = projectm_create();
    if (handle == nullptr) {
        throw std::runtime_error("Failed to create projectM instance");
    }
    return handle;
}

} // namespace platyplaty
