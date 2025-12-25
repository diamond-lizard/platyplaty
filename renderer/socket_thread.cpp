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

namespace {

constexpr int kPollTimeoutMs = 100;

// Reject a pending connection on the server socket (defensive).
void reject_second_client(ServerSocket& server) {
    int second_fd = server.accept_client();
    if (second_fd >= 0) {
        ::close(second_fd);
    }
}

// Send error response for a failed parse.
void send_parse_error(ClientSocket& client, const CommandParseResult& result) {
    Response resp;
    resp.id = result.command.id;
    resp.success = false;
    resp.error = result.error;
    client.send(serialize_response(resp));
}

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

// Returns true to continue, false to break client loop.
bool SocketThread::process_message(ClientSocket& client) {
    auto payload = client.recv();
    if (!payload.has_value()) {
        if (client.has_framing_error()) {
            emit_stderr_event("DISCONNECT", client.framing_error());
        }
        return false;
    }

    auto result = parse_command(*payload);
    if (!result.success) {
        send_parse_error(client, result);
        return true;
    }

    m_slot.put_command(std::move(result.command));

    Response resp;
    if (!m_slot.wait_for_response(resp, std::chrono::milliseconds(kPollTimeoutMs))) {
        return true;
    }
    if (!client.send(serialize_response(resp))) {
        emit_stderr_event("DISCONNECT", "write failed");
        return false;
    }
    return true;
}

// Returns true to continue loop, false to break.
bool SocketThread::poll_and_process(ClientSocket& client) {
    pollfd pfds[2]{};
    pfds[0].fd = m_server.get_fd();
    pfds[0].events = POLLIN;
    pfds[1].fd = client.get_fd();
    pfds[1].events = POLLIN;

    int ret = poll(pfds, 2, kPollTimeoutMs);
    if (ret < 0 && errno != EINTR) {
        return false;
    }
    if (ret <= 0) {
        return true;
    }

    if ((pfds[0].revents & POLLIN) != 0) {
        reject_second_client(m_server);
    }
    if ((pfds[1].revents & (POLLHUP | POLLERR)) != 0) {
        return false;
    }
    if ((pfds[1].revents & POLLIN) != 0 && !process_message(client)) {
        return false;
    }
    return true;
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

    if (!m_initialized.load()) {
        emit_stderr_event("DISCONNECT", "client disconnected before INIT");
    }
}

}  // namespace platyplaty
