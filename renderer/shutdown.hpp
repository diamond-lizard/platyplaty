// shutdown.hpp - Shutdown flag and signal setup for Platyplaty renderer
// Provides atomic shutdown flag checked by the main loop and signal
// handlers for SIGINT, SIGTERM, and SIGHUP.

#ifndef PLATYPLATY_SHUTDOWN_HPP
#define PLATYPLATY_SHUTDOWN_HPP

#include <atomic>

namespace platyplaty {

// Atomic shutdown flag. Signal handlers set this to true.
// The main loop checks this flag each iteration.
extern std::atomic<bool> g_shutdown_requested;

// Install signal handlers for SIGINT, SIGTERM, SIGHUP.
// Also ignores SIGPIPE to allow socket errors to be handled via return codes.
// Call once at program startup before any other initialization.
void setup_signal_handlers();

} // namespace platyplaty

#endif // PLATYPLATY_SHUTDOWN_HPP
