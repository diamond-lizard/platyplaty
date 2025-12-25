// command_handler.hpp - Command dispatch for post-INIT commands.
// Handles LOAD_PRESET, SHOW_WINDOW, SET_FULLSCREEN, QUIT.

#ifndef PLATYPLATY_COMMAND_HANDLER_HPP
#define PLATYPLATY_COMMAND_HANDLER_HPP

#include "protocol.hpp"

namespace platyplaty {

class Visualizer;
class Window;

// Handle a command received after INIT.
// Returns a Response to send back to the client.
Response handle_command(const Command& cmd, Visualizer& viz, Window& win, bool& running);

}  // namespace platyplaty

#endif  // PLATYPLATY_COMMAND_HANDLER_HPP
