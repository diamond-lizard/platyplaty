// command_handler.cpp - Command dispatch for post-INIT commands.
#include "command_handler.hpp"
#include "shutdown.hpp"
#include "visualizer.hpp"
#include "window.hpp"
#include "audio_capture.hpp"

namespace platyplaty {

Response handle_command(
    const Command& cmd,
    Visualizer& viz,
    Window& win,
    bool& running,
    const AudioCapture& audio) {
    Response resp{};
    resp.id = cmd.id;

    switch (cmd.type) {
    case CommandType::LOAD_PRESET: {
        if (cmd.preset_path.empty()) {
            resp.success = false;
            resp.error = "empty path";
            break;
        }
        if (cmd.preset_path != "idle://" && cmd.preset_path[0] != '/') {
            resp.success = false;
            resp.error = "relative path not allowed: " + cmd.preset_path;
            break;
        }
        auto result = viz.load_preset(cmd.preset_path);
        resp.success = result.success;
        if (result.success) {
            resp.data = nlohmann::json::object();
        } else {
            resp.error = result.error_message;
        }
        break;
    }
    case CommandType::SHOW_WINDOW:
        win.show();
        resp.success = true;
        resp.data = nlohmann::json::object();
        break;

    case CommandType::SET_FULLSCREEN:
        if (!win.is_visible()) {
            resp.success = false;
            resp.error = "window not visible";
            break;
        }
        win.set_fullscreen(cmd.fullscreen_enabled);
        resp.success = true;
        resp.data = nlohmann::json::object();
        break;

    case CommandType::QUIT:
        running = false;
        g_shutdown_requested.store(true, std::memory_order_relaxed);
        resp.success = true;
        resp.data = nlohmann::json::object();
        break;

    case CommandType::CHANGE_AUDIO_SOURCE:
        resp.success = false;
        resp.error = "cannot change audio source after INIT";
        break;

    case CommandType::GET_STATUS: {
        nlohmann::json data;
        data["audio_source"] = audio.get_source();
        data["audio_connected"] = audio.is_connected();
        data["preset_path"] = viz.get_current_preset_path();
        data["visible"] = win.is_visible();
        data["fullscreen"] = win.is_fullscreen();
        resp.success = true;
        resp.data = data;
        break;
    }

    case CommandType::INIT:
        resp.success = false;
        resp.error = "already initialized";
        break;

    case CommandType::UNKNOWN:
    default:
        resp.success = false;
        resp.error = "unknown command";
        break;
    }

    return resp;
}

}  // namespace platyplaty
