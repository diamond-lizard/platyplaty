// Socket thread implementation.

#include "socket_thread.hpp"
#include "client_socket.hpp"
#include "netstring.hpp"
#include "protocol.hpp"
#include "shutdown.hpp"
#include "stderr_event.hpp"

#include <poll.h>
#include <unistd.h>

namespace platyplaty {

SocketThread::SocketThread(const std::string& socket_path, CommandSlot& slot)
    : m_server(socket_path)
    , m_slot(slot) {
}

SocketThread::~SocketThread() {
    if (m_thread.joinable()) {
        m_thread.join();
    }
}

void SocketThread::start() {
    m_thread = std::thread(&SocketThread::thread_main, this);
}

void SocketThread::join() {
    if (m_thread.joinable()) {
        m_thread.join();
    }
}

void SocketThread::thread_main() {
    while (!g_shutdown_requested.load()) {
        // Poll the listening socket for incoming connections.
        pollfd pfd{};
        pfd.fd = m_server.get_fd();
        pfd.events = POLLIN;

        int ret = poll(&pfd, 1, 100);  // 100ms timeout
        if (ret < 0) {
            if (errno == EINTR) {
                continue;
            }
            break;  // Poll error
        }
        if (ret == 0) {
            continue;  // Timeout, check shutdown flag
        }

        if ((pfd.revents & POLLIN) != 0) {
            handle_client();
        }
    }
}

void SocketThread::handle_client() {
    int client_fd = m_server.accept_client();
    if (client_fd < 0) {
        return;
    }

    ClientSocket client(client_fd);

    while (!g_shutdown_requested.load() && client.is_open()) {
        // Poll both listening socket (to reject second clients) and client
        pollfd pfds[2]{};
        pfds[0].fd = m_server.get_fd();
        pfds[0].events = POLLIN;
        pfds[1].fd = client.get_fd();
        pfds[1].events = POLLIN;

        int ret = poll(pfds, 2, 100);
        if (ret < 0) {
            if (errno == EINTR) {
                continue;
            }
            break;
        }
        if (ret == 0) {
            continue;
        }

        // Reject second client connections (defensive).
        if ((pfds[0].revents & POLLIN) != 0) {
            int second_fd = m_server.accept_client();
            if (second_fd >= 0) {
                ::close(second_fd);
            }
        }

        // Handle client data.
        if ((pfds[1].revents & POLLIN) != 0) {
            auto payload = client.recv();
            if (!payload.has_value()) {
                if (client.has_framing_error()) {
                    emit_stderr_event("DISCONNECT", client.framing_error());
                }
                break;  // Client disconnected or framing error
            }

            // Parse command.
            auto result = parse_command(*payload);
            if (!result.success) {
                Response resp;
                resp.id = result.command.id;
                resp.success = false;
                resp.error = result.error;
                client.send(serialize_response(resp));
                continue;
            }

            // Put command in slot and wait for response.
            m_slot.put_command(std::move(result.command));

            Response resp;
            if (m_slot.wait_for_response(resp, std::chrono::milliseconds(100))) {
                if (!client.send(serialize_response(resp))) {
                    emit_stderr_event("DISCONNECT", "write failed");
                    break;
                }
            }
        }

        // Check for client disconnect (POLLHUP/POLLERR).
        if ((pfds[1].revents & (POLLHUP | POLLERR)) != 0) {
            break;
        }
    }

    // Client disconnected. If not initialized, stay alive for new client.
    if (!m_initialized.load()) {
        emit_stderr_event("DISCONNECT", "client disconnected before INIT");
    }
}

}  // namespace platyplaty
