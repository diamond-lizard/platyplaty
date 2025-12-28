// Protocol types for socket IPC.
// Defines commands, responses, and JSON serialization.

#ifndef PLATYPLATY_PROTOCOL_HPP
#define PLATYPLATY_PROTOCOL_HPP

#include <nlohmann/json.hpp>
#include <optional>
#include <string>

namespace platyplaty {

enum class CommandType {
    CHANGE_AUDIO_SOURCE,
    INIT,
    LOAD_PRESET,
    SHOW_WINDOW,
    SET_FULLSCREEN,
    QUIT,
    GET_STATUS,
    UNKNOWN
};

struct Command {
    CommandType type{CommandType::UNKNOWN};
    std::optional<int> id{std::nullopt};
    std::string audio_source{};
    std::string preset_path{};
    bool fullscreen_enabled{false};
};

struct Response {
    std::optional<int> id{std::nullopt};
    bool success{false};
    nlohmann::json data{};
    std::string error{};
};

struct CommandParseResult {
    bool success{false};
    Command command{};
    std::string error{};
};

// Parse a JSON string into a Command structure.
// Returns error if JSON is malformed or fields are invalid.
CommandParseResult parse_command(const std::string& json);

// Serialize a Response to JSON string.
std::string serialize_response(const Response& response);

}  // namespace platyplaty

#endif  // PLATYPLATY_PROTOCOL_HPP
