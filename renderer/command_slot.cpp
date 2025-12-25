// Command slot implementation.

#include "command_slot.hpp"

namespace platyplaty {

bool CommandSlot::put_command(Command cmd) {
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_command = std::move(cmd);
        m_response.reset();
    }
    m_cv.notify_one();
    return true;
}

std::optional<Command> CommandSlot::try_get_command() {
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!m_command.has_value()) {
        return std::nullopt;
    }
    Command cmd = std::move(*m_command);
    m_command.reset();
    return cmd;
}

void CommandSlot::put_response(Response resp) {
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_response = std::move(resp);
    }
    m_cv.notify_one();
}

bool CommandSlot::wait_for_response(Response& out,
                                        std::chrono::milliseconds timeout) {
    std::unique_lock<std::mutex> lock(m_mutex);
    bool got_response = m_cv.wait_for(lock, timeout, [this] {
        return m_response.has_value();
    });
    if (got_response) {
        out = std::move(*m_response);
        m_response.reset();
        return true;
    }
    return false;
}

}  // namespace platyplaty
