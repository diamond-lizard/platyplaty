// RAII Unix domain socket server implementation.

#include "server_socket.hpp"
#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

namespace platyplaty {

ServerSocket::ServerSocket(const std::string& path) : m_path{path} {
    m_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (m_fd < 0) {
        throw std::runtime_error{"socket(): " + std::string{strerror(errno)}};
    }

    sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    if (path.size() >= sizeof(addr.sun_path)) {
        close(m_fd);
        throw std::runtime_error{"socket path too long"};
    }
    strncpy(addr.sun_path, path.c_str(), sizeof(addr.sun_path) - 1);

    if (bind(m_fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        close(m_fd);
        throw std::runtime_error{"bind(): " + std::string{strerror(errno)}};
    }

    if (listen(m_fd, 1) < 0) {
        close(m_fd);
        unlink(path.c_str());
        throw std::runtime_error{"listen(): " + std::string{strerror(errno)}};
    }
}

ServerSocket::ServerSocket(ServerSocket&& other) noexcept
    : m_fd{other.m_fd}, m_path{std::move(other.m_path)} {
    other.m_fd = -1;
}

ServerSocket& ServerSocket::operator=(ServerSocket&& other) noexcept {
    if (this != &other) {
        if (m_fd >= 0) {
            close(m_fd);
            unlink(m_path.c_str());
        }
        m_fd = other.m_fd;
        m_path = std::move(other.m_path);
        other.m_fd = -1;
    }
    return *this;
}

ServerSocket::~ServerSocket() {
    if (m_fd >= 0) {
        close(m_fd);
        unlink(m_path.c_str());
    }
}

int ServerSocket::accept_client() {
    const int client_fd = accept(m_fd, nullptr, nullptr);
    if (client_fd < 0) {
        throw std::runtime_error{"accept(): " + std::string{strerror(errno)}};
    }
    return client_fd;
}

}  // namespace platyplaty
