// Client socket implementation with netstring framing.

#include "client_socket.hpp"
#include "netstring.hpp"
#include <array>
#include <unistd.h>

namespace platyplaty {

namespace {
constexpr std::size_t RECV_BUFFER_SIZE = 4096;
}  // namespace

ClientSocket::ClientSocket(int fd) : m_fd{fd} {}

ClientSocket::ClientSocket(ClientSocket&& other) noexcept
    : m_fd{other.m_fd},
      m_buffer{std::move(other.m_buffer)},
      m_framing_error{other.m_framing_error},
      m_error_msg{std::move(other.m_error_msg)} {
    other.m_fd = -1;
}

ClientSocket& ClientSocket::operator=(ClientSocket&& other) noexcept {
    if (this != &other) {
        close();
        m_fd = other.m_fd;
        m_buffer = std::move(other.m_buffer);
        m_framing_error = other.m_framing_error;
        m_error_msg = std::move(other.m_error_msg);
        other.m_fd = -1;
    }
    return *this;
}

ClientSocket::~ClientSocket() {
    close();
}

bool ClientSocket::send(const std::string& payload) {
    if (m_fd < 0) return false;

    const std::string netstr = serialize_netstring(payload);
    const char* data = netstr.data();
    std::size_t remaining = netstr.size();

    while (remaining > 0) {
        const ssize_t written = ::write(m_fd, data, remaining);
        if (written <= 0) return false;
        data += written;
        remaining -= static_cast<std::size_t>(written);
    }
    return true;
}

std::optional<std::string> ClientSocket::recv() {
    if (m_fd < 0 || m_framing_error) return std::nullopt;

    // Try to parse from existing buffer first
    std::size_t consumed = 0;
    auto result = parse_netstring(m_buffer, consumed);

    if (result.success) {
        m_buffer.erase(0, consumed);
        return result.payload;
    }

    // Check for framing error (not just incomplete)
    if (!result.error.empty() &&
        result.error.find("invalid") != std::string::npos) {
        m_framing_error = true;
        m_error_msg = result.error;
        return std::nullopt;
    }

    // Need more data
    std::array<char, RECV_BUFFER_SIZE> buf;
    const ssize_t n = ::read(m_fd, buf.data(), buf.size());

    if (n <= 0) return std::nullopt;  // EOF or error

    m_buffer.append(buf.data(), static_cast<std::size_t>(n));

    // Try parsing again
    consumed = 0;
    result = parse_netstring(m_buffer, consumed);

    if (result.success) {
        m_buffer.erase(0, consumed);
        return result.payload;
    }

    if (!result.error.empty() &&
        result.error.find("invalid") != std::string::npos) {
        m_framing_error = true;
        m_error_msg = result.error;
    }

    return std::nullopt;
}

void ClientSocket::close() {
    if (m_fd >= 0) {
        ::close(m_fd);
        m_fd = -1;
    }
}

}  // namespace platyplaty
