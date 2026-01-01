// Key event handling for Platyplaty renderer.
// Rate-limits key repeats and emits KEY_PRESSED events to stderr.

#ifndef PLATYPLATY_KEY_EVENT_HPP
#define PLATYPLATY_KEY_EVENT_HPP

#include <chrono>
#include <string>
#include <unordered_map>

namespace platyplaty {

// Rate limiting interval for key repeat events (500ms).
constexpr auto KEY_REPEAT_INTERVAL = std::chrono::milliseconds(500);

// Tracks last emit time per key for rate limiting.
// Key identity includes modifiers, so "control-n" and "n" are separate.
class KeyRateLimiter {
public:
    // Check if event should be emitted and update timestamp if so.
    // Returns true if the event should be emitted.
    // is_repeat: true if SDL reports this as a repeat event.
    bool should_emit(const std::string& key_name, bool is_repeat);

private:
    using Clock = std::chrono::steady_clock;
    std::unordered_map<std::string, Clock::time_point> m_last_emit;
};

}  // namespace platyplaty

#endif  // PLATYPLATY_KEY_EVENT_HPP
