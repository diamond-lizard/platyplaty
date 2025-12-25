// RAII wrapper for client socket connections.
// Handles send/recv with netstring framing.

#ifndef PLATYPLATY_CLIENT_SOCKET_HPP
#define PLATYPLATY_CLIENT_SOCKET_HPP

#include <optional>
#include <string>

namespace platyplaty {

class ClientSocket {
public:
    // Wrap an existing file descriptor (from accept()).
    explicit ClientSocket(int fd);

    // Non-copyable
    ClientSocket(const ClientSocket&) = delete;
    ClientSocket& operator=(const ClientSocket&) = delete;

    // Movable
    ClientSocket(ClientSocket&& other) noexcept;
    ClientSocket& operator=(ClientSocket&& other) noexcept;

    // Close the socket.
    ~ClientSocket();

    // Send a payload as a netstring. Returns true on success.
    bool send(const std::string& payload);

    // Receive the next complete netstring payload.
    // Returns nullopt if connection closed or incomplete data.
    // Returns error string on framing error.
    std::optional<std::string> recv();

    // Check if there was a framing error on last recv.
    bool has_framing_error() const { return m_framing_error; }

    // Get the last framing error message.
    const std::string& framing_error() const { return m_error_msg; }

    // Get the file descriptor.
    int get_fd() const { return m_fd; }

    // Close the socket explicitly.
    void close();

    // Check if socket is open.
    bool is_open() const { return m_fd >= 0; }

private:
    int m_fd{-1};
    std::string m_buffer{};
    bool m_framing_error{false};
    std::string m_error_msg{};
};

}  // namespace platyplaty

#endif  // PLATYPLATY_CLIENT_SOCKET_HPP
