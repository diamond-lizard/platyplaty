// shutdown.cpp - Signal handler implementation for Platyplaty renderer

#include "shutdown.hpp"
#include <csignal>

namespace platyplaty {

std::atomic<bool> g_shutdown_requested{false};

namespace {

void signal_handler(int /*signal*/) {
    g_shutdown_requested.store(true, std::memory_order_relaxed);
}

} // anonymous namespace

void setup_signal_handlers() {
    std::signal(SIGPIPE, SIG_IGN);
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);
    std::signal(SIGHUP, signal_handler);
}

} // namespace platyplaty
