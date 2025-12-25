// main.cpp - Entry point for Platyplaty renderer
// Stage 2: Socket IPC, audio capture, two-phase initialization.

#include "shutdown.hpp"
#include "event_loop.hpp"
#include "visualizer.hpp"
#include "window.hpp"
#include "command_slot.hpp"
#include "socket_thread.hpp"
#include "audio_capture.hpp"
#include <cstdlib>
#include <iostream>
#include <cstring>
#include <cstdio>
#include <string>
#include <thread>
#include <optional>

namespace {
constexpr char const* PRESET_PATH = "presets/test/101-per_frame.milk";

// Static storage for socket path (needed by atexit handler).
std::string g_socket_path;

// atexit handler to unlink socket file.
void cleanup_socket() {
    if (!g_socket_path.empty()) {
        std::remove(g_socket_path.c_str());
    }
}

// Wait for INIT command, collecting audio source along the way.
// Returns audio source string, or empty string if shutdown requested.
// Process single pre-init command. Returns audio source on successful INIT,
// nullopt to continue waiting.
std::optional<std::string> process_preinit_command(
        const platyplaty::Command& cmd,
        platyplaty::CommandSlot& slot,
        std::string& audio_source) {
    platyplaty::Response resp{};
    resp.id = cmd.id;
    resp.success = false;

    if (cmd.type == platyplaty::CommandType::CHANGE_AUDIO_SOURCE) {
        audio_source = cmd.audio_source;
        resp.success = true;
        resp.data = nlohmann::json::object();
    } else if (cmd.type == platyplaty::CommandType::INIT && !audio_source.empty()) {
        resp.success = true;
        resp.data = nlohmann::json::object();
        slot.put_response(resp);
        return audio_source;
    } else if (cmd.type == platyplaty::CommandType::INIT) {
        resp.error = "audio source not set";
    } else {
        resp.error = "command not allowed before INIT";
    }
    slot.put_response(resp);
    return std::nullopt;
}

// Wait for INIT command, collecting audio source along the way.
// Returns audio source string, or empty string if shutdown requested.
std::string wait_for_init(platyplaty::CommandSlot& slot) {
    std::string audio_source;
    while (!platyplaty::g_shutdown_requested.load()) {
        auto cmd_opt = slot.try_get_command();
        if (!cmd_opt) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            continue;
        }
        auto result = process_preinit_command(*cmd_opt, slot, audio_source);
        if (result) {
            return *result;
        }
    }
    return "";
}
} // anonymous namespace

int main(int argc, const char* argv[]) {
    platyplaty::setup_signal_handlers();

    // Parse command-line arguments
    if (argc != 3 || std::strcmp(argv[1], "--socket-path") != 0) {
        std::cerr << "Usage: " << argv[0] << " --socket-path <path>\n";
        return EXIT_FAILURE;
    }
    const char* socket_path = argv[2];

    // Phase 1: Store socket path and register cleanup
    g_socket_path = socket_path;
    std::atexit(cleanup_socket);

    // Phase 1: Create command slot and socket thread
    platyplaty::CommandSlot command_slot;
    platyplaty::SocketThread socket_thread{g_socket_path, command_slot};
    socket_thread.start();

    // Phase 1: Signal ready to client
    std::cout << "SOCKET READY\n" << std::flush;

    // Pre-init loop: wait for CHANGE AUDIO SOURCE and INIT
    std::string audio_source = wait_for_init(command_slot);

    // Check if we exited due to shutdown
    if (platyplaty::g_shutdown_requested.load()) {
        socket_thread.join();
        return EXIT_SUCCESS;
    }

    try {
        platyplaty::Window window;
        auto [width, height] = window.get_drawable_size();
        platyplaty::Visualizer visualizer(width, height);

        // Create audio capture with the configured source
        platyplaty::AudioCapture audio_capture{audio_source, visualizer};
        audio_capture.start();

        auto result = visualizer.load_preset(PRESET_PATH);
        if (!result.success) {
            std::cerr << "Warning: Failed to load preset: " << result.error_message << '\n';
        }

        platyplaty::run_event_loop(window, visualizer, command_slot);

        // Shutdown sequence: audio thread, then socket thread
        audio_capture.stop();
        audio_capture.join();
        socket_thread.join();
        return EXIT_SUCCESS;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
}
