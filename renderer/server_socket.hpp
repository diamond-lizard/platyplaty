// RAII wrapper for Unix domain socket server.
// Creates, binds, and listens on a socket; cleans up on destruction.

#ifndef PLATYPLATY_SERVER_SOCKET_HPP
#define PLATYPLATY_SERVER_SOCKET_HPP

#include <string>

namespace platyplaty {

class ServerSocket {
public:
    // Create and bind a Unix domain socket at the given path.
    // Throws std::runtime_error on failure.
    explicit ServerSocket(const std::string& path);

    // Non-copyable
    ServerSocket(const ServerSocket&) = delete;
    ServerSocket& operator=(const ServerSocket&) = delete;

    // Movable
    ServerSocket(ServerSocket&& other) noexcept;
    ServerSocket& operator=(ServerSocket&& other) noexcept;

    // Close socket and unlink path.
    ~ServerSocket();

    // Accept a client connection. Blocks until a client connects.
    // Returns the client file descriptor.
    // Throws std::runtime_error on failure.
    int accept_client();

    // Get the listening socket file descriptor.
    int get_fd() const { return m_fd; }

    // Get the socket path.
    const std::string& get_path() const { return m_path; }

private:
    int m_fd{-1};
    std::string m_path{};
};

}  // namespace platyplaty

#endif  // PLATYPLATY_SERVER_SOCKET_HPP
