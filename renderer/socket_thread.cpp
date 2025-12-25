// Socket thread implementation.

#include "socket_thread.hpp"
#include "client_socket.hpp"
#include "shutdown.hpp"
#include "stderr_event.hpp"

#include <poll.h>

namespace platyplaty {

namespace {
constexpr int kPollTimeoutMs = 100;
}  // namespace


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
        pollfd pfd{};
        pfd.fd = m_server.get_fd();
        pfd.events = POLLIN;

        int ret = poll(&pfd, 1, kPollTimeoutMs);
        if (ret < 0 && errno != EINTR) {
            break;
        }
        if (ret <= 0) {
            continue;
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
        if (!poll_and_process(client)) {
            break;
        }
    }

    // Emit DISCONNECT event for clean EOF (framing errors already emitted above).
    // Different message for pre-INIT vs post-INIT per architecture doc.
    if (!client.has_framing_error()) {
        if (m_initialized.load()) {
            emit_stderr_event("DISCONNECT", "client disconnected");
        } else {
            emit_stderr_event("DISCONNECT", "client disconnected before INIT");
        }
    }
}

}  // namespace platyplaty
