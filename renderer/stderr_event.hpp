// Stderr event emission for asynchronous notifications.
// Events are netstring-framed JSON written to stderr.

#ifndef PLATYPLATY_STDERR_EVENT_HPP
#define PLATYPLATY_STDERR_EVENT_HPP

#include "netstring.hpp"
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>

namespace platyplaty {

// Emit an event to stderr in netstring-framed JSON format.
// Event types: DISCONNECT, AUDIO_ERROR, QUIT
inline void emit_stderr_event(
    const std::string& event_type,
    const std::string& reason) {

    nlohmann::json j;
    j["source"] = "PLATYPLATY";
    j["event"] = event_type;
    j["reason"] = reason;

    std::cerr << serialize_netstring(j.dump()) << std::flush;
}

}  // namespace platyplaty

#endif  // PLATYPLATY_STDERR_EVENT_HPP
