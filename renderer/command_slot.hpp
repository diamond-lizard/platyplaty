// Command slot for thread-safe command handoff.
// Single-slot design: socket thread puts commands, main thread gets them.

#ifndef PLATYPLATY_COMMAND_SLOT_HPP
#define PLATYPLATY_COMMAND_SLOT_HPP

#include "protocol.hpp"

#include <chrono>
#include <condition_variable>
#include <mutex>
#include <optional>

namespace platyplaty {

// Thread-safe single-slot for passing commands from socket thread
// to main thread and receiving responses back.
class CommandSlot {
public:
    CommandSlot() = default;

    // Non-copyable and non-movable (contains mutex/cv).
    CommandSlot(const CommandSlot&) = delete;
    CommandSlot& operator=(const CommandSlot&) = delete;
    CommandSlot(CommandSlot&&) = delete;
    CommandSlot& operator=(CommandSlot&&) = delete;

    // Socket thread: put command and wait for response.
    // Blocks until response arrives or shutdown requested.
    // Returns true if response received, false on shutdown.
    bool put_command(Command cmd);

    // Main thread: check for pending command (non-blocking).
    std::optional<Command> try_get_command();

    // Main thread: provide response to waiting socket thread.
    void put_response(Response resp);

    // Socket thread: wait for response with timeout.
    // Returns true if response received, false on timeout.
    bool wait_for_response(Response& out, std::chrono::milliseconds timeout);

private:
    std::mutex m_mutex{};
    std::condition_variable m_cv{};
    std::optional<Command> m_command{std::nullopt};
    std::optional<Response> m_response{std::nullopt};
};

}  // namespace platyplaty

#endif  // PLATYPLATY_COMMAND_SLOT_HPP
