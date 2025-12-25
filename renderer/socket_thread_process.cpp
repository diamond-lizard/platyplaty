// Socket thread message processing implementation.

#include "socket_thread.hpp"
#include "client_socket.hpp"
#include "netstring.hpp"
#include "protocol.hpp"
#include "shutdown.hpp"
#include "stderr_event.hpp"

#include <array>
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
    bool got_response = false;
    while (!g_shutdown_requested.load()) {
        if (m_slot.wait_for_response(resp, std::chrono::milliseconds(kPollTimeoutMs))) {
            got_response = true;
            break;
        }
    }
    if (!got_response) {
        return false;
    }
    if (!client.send(serialize_response(resp))) {
        emit_stderr_event("DISCONNECT", "write failed");
        return false;
    }
    return true;
}

// Returns true to continue loop, false to break.
bool SocketThread::poll_and_process(ClientSocket& client) {
    std::array<pollfd, 2> pfds{};
    pfds[0].fd = m_server.get_fd();
    pfds[0].events = POLLIN;
    pfds[1].fd = client.get_fd();
    pfds[1].events = POLLIN;

    int ret = poll(pfds.data(), 2, kPollTimeoutMs);
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

}  // namespace platyplaty
