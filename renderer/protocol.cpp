// Protocol JSON parsing and serialization implementation.

#include "protocol.hpp"
#include <set>

namespace platyplaty {

namespace {

const std::set<std::string> VALID_COMMANDS = {
    "CHANGE AUDIO SOURCE", "INIT", "LOAD PRESET",
    "SHOW WINDOW", "SET FULLSCREEN", "QUIT", "GET STATUS"
};

CommandType string_to_command_type(const std::string& cmd) {
    if (cmd == "CHANGE AUDIO SOURCE") return CommandType::CHANGE_AUDIO_SOURCE;
    if (cmd == "INIT") return CommandType::INIT;
    if (cmd == "LOAD PRESET") return CommandType::LOAD_PRESET;
    if (cmd == "SHOW WINDOW") return CommandType::SHOW_WINDOW;
    if (cmd == "SET FULLSCREEN") return CommandType::SET_FULLSCREEN;
    if (cmd == "QUIT") return CommandType::QUIT;
    if (cmd == "GET STATUS") return CommandType::GET_STATUS;
    return CommandType::UNKNOWN;
}

// Allowed fields per command type (excluding "command" and "id")
const std::set<std::string>& allowed_fields(CommandType type) {
    static const std::set<std::string> audio_fields = {"audio_source"};
    static const std::set<std::string> empty_fields = {};
    static const std::set<std::string> preset_fields = {"path"};
    static const std::set<std::string> fullscreen_fields = {"enabled"};

    switch (type) {
        case CommandType::CHANGE_AUDIO_SOURCE: return audio_fields;
        case CommandType::LOAD_PRESET: return preset_fields;
        case CommandType::SET_FULLSCREEN: return fullscreen_fields;
        case CommandType::GET_STATUS: return empty_fields;
        default: return empty_fields;
    }
}

std::string parse_audio_source(const nlohmann::json& j, Command& cmd) {
    if (!j.contains("audio_source") || !j["audio_source"].is_string()) {
        return "CHANGE AUDIO SOURCE requires 'audio_source' string";
    }
    cmd.audio_source = j["audio_source"].get<std::string>();
    return "";
}

std::string parse_preset_path(const nlohmann::json& j, Command& cmd) {
    if (!j.contains("path") || !j["path"].is_string()) {
        return "LOAD PRESET requires 'path' string";
    }
    cmd.preset_path = j["path"].get<std::string>();
    return "";
}

std::string parse_fullscreen(const nlohmann::json& j, Command& cmd) {
    if (!j.contains("enabled") || !j["enabled"].is_boolean()) {
        return "SET FULLSCREEN requires 'enabled' boolean";
    }
    cmd.fullscreen_enabled = j["enabled"].get<bool>();
    return "";
}

}  // namespace

CommandParseResult parse_command(const std::string& json_str) {
    nlohmann::json j;

    try {
        j = nlohmann::json::parse(json_str);
    } catch (const nlohmann::json::parse_error& e) {
        return {false, {}, std::string{"JSON parse error: "} + e.what()};
    }

    if (!j.is_object()) {
        return {false, {}, "expected JSON object"};
    }

    // Check for "command" field
    if (!j.contains("command") || !j["command"].is_string()) {
        return {false, {}, "missing or invalid 'command' field"};
    }

    const std::string cmd_str = j["command"].get<std::string>();
    const CommandType type = string_to_command_type(cmd_str);

    if (type == CommandType::UNKNOWN) {
        return {false, {}, "unknown command: " + cmd_str};
    }

    Command cmd;
    cmd.type = type;

    // Parse "id" field (required for all commands)
    if (!j.contains("id")) {
        return {false, {}, "missing 'id' field"};
    }
    if (!j["id"].is_number_integer()) {
        return {false, {}, "'id' must be an integer"};
    }
    cmd.id = j["id"].get<int>();

    // Get allowed fields for this command type
    const auto& allowed = allowed_fields(type);

    // Check for unknown fields
    for (const auto& [key, value] : j.items()) {
        if (key == "command" || key == "id") continue;
        if (allowed.find(key) == allowed.end()) {
            return {false, {}, "unexpected field: " + key};
        }
    }

    // Parse command-specific fields
    std::string field_error;
    switch (type) {
        case CommandType::CHANGE_AUDIO_SOURCE:
            field_error = parse_audio_source(j, cmd);
            break;
        case CommandType::LOAD_PRESET:
            field_error = parse_preset_path(j, cmd);
            break;
        case CommandType::SET_FULLSCREEN:
            field_error = parse_fullscreen(j, cmd);
            break;
        default:
            break;
    }
    if (!field_error.empty()) {
        return {false, {}, field_error};
    }
    return {true, cmd, ""};
}

std::string serialize_response(const Response& response) {
    nlohmann::json j;

    if (response.id.has_value()) {
        j["id"] = response.id.value();
    } else {
        j["id"] = nullptr;
    }

    j["success"] = response.success;

    if (response.success) {
        j["data"] = response.data;
    } else {
        j["error"] = response.error;
    }

    return j.dump();
}

}  // namespace platyplaty
