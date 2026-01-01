// Key event handling implementation for Platyplaty renderer.

#include "key_event.hpp"

namespace platyplaty {

bool KeyRateLimiter::should_emit(const std::string& key_name, bool is_repeat) {
    auto now = Clock::now();

    // Initial keydowns (not repeats) always pass through.
    if (!is_repeat) {
        m_last_emit[key_name] = now;
        return true;
    }

    // For repeat events, check rate limit.
    auto it = m_last_emit.find(key_name);
    if (it == m_last_emit.end()) {
        // No previous emit recorded; allow and record.
        m_last_emit[key_name] = now;
        return true;
    }

    auto elapsed = now - it->second;
    if (elapsed >= KEY_REPEAT_INTERVAL) {
        it->second = now;
        return true;
    }

    return false;
}

}  // namespace platyplaty
