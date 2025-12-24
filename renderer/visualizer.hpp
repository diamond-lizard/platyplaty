// visualizer.hpp - ProjectM visualization wrapper for Platyplaty renderer
// RAII class that manages projectM instance lifecycle and preset loading.

#ifndef PLATYPLATY_VISUALIZER_HPP
#define PLATYPLATY_VISUALIZER_HPP

#include <projectM-4/projectM.h>
#include <cstddef>
#include <string>

namespace platyplaty {

// Result of a preset load attempt.
struct PresetLoadResult {
    bool success{false};
    std::string error_message;
};

// RAII wrapper for projectM visualization instance.
// Throws std::runtime_error if initialization fails.
class Visualizer {
public:
    // Create visualizer with initial drawable size. Throws on failure.
    explicit Visualizer(std::size_t width, std::size_t height);

    // Non-copyable
    Visualizer(const Visualizer&) = delete;
    Visualizer& operator=(const Visualizer&) = delete;

    // Non-movable
    Visualizer(Visualizer&&) = delete;
    Visualizer& operator=(Visualizer&&) = delete;

    // Cleanup projectM instance
    ~Visualizer();

    // Update viewport size (call on window resize)
    void set_window_size(std::size_t width, std::size_t height);

    // Render a single frame
    void render_frame();

    // Load preset from file path. Returns success/failure with error.
    PresetLoadResult load_preset(const std::string& path);

private:
    static void preset_switch_failed_callback(
        const char* preset_filename,
        const char* message,
        void* user_data);

    // Helper to create projectM instance; throws on failure.
    static projectm_handle create_projectm_instance();

    projectm_handle handle_{nullptr};
    static constexpr std::size_t ERROR_BUFFER_SIZE = 32768;
    char error_buffer_[ERROR_BUFFER_SIZE]{};
};

} // namespace platyplaty

#endif // PLATYPLATY_VISUALIZER_HPP
