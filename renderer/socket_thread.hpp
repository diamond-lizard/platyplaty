// Socket thread for handling client connections.
// Accepts one client, processes commands via CommandSlot.

#ifndef PLATYPLATY_SOCKET_THREAD_HPP
#define PLATYPLATY_SOCKET_THREAD_HPP

#include "command_slot.hpp"
#include "server_socket.hpp"

#include <atomic>
#include <string>
#include <thread>

namespace platyplaty {

// Thread that manages the server socket and client communication.
// Accepts one client at a time, rejects additional connections.
class SocketThread {
public:
    // Create socket thread with given socket path and command slot.
    SocketThread(const std::string& socket_path, CommandSlot& slot);

    // Non-copyable and non-movable.
    SocketThread(const SocketThread&) = delete;
    SocketThread& operator=(const SocketThread&) = delete;
    SocketThread(SocketThread&&) = delete;
    SocketThread& operator=(SocketThread&&) = delete;

    ~SocketThread();

    // Start the socket thread.
    void start();

    // Wait for thread to finish.
    void join();

    // Check if renderer has been initialized (INIT command received).
    bool is_initialized() const { return m_initialized.load(); }

    // Set initialized state (called by main thread after INIT).
    void set_initialized(bool value) { m_initialized.store(value); }

private:
    void thread_main();
    void handle_client();

    ServerSocket m_server;
    CommandSlot& m_slot;
    std::thread m_thread{};
    std::atomic<bool> m_initialized{false};
};

}  // namespace platyplaty

#endif  // PLATYPLATY_SOCKET_THREAD_HPP
