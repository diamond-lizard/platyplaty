// event_loop.hpp - Main render loop for Platyplaty renderer
// Polls SDL events, renders frames, and handles window resize.

#ifndef PLATYPLATY_EVENT_LOOP_HPP
#define PLATYPLATY_EVENT_LOOP_HPP

namespace platyplaty {

class Window;
class Visualizer;

// Run the main event loop until shutdown is requested.
// Polls SDL events, clears buffers, renders frames, and swaps buffers.
void run_event_loop(Window& window, Visualizer& visualizer);

} // namespace platyplaty

#endif // PLATYPLATY_EVENT_LOOP_HPP
