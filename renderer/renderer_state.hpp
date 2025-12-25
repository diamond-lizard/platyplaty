// Renderer state tracking for two-phase initialization.
// Tracks whether renderer is waiting for config, init, or running.

#ifndef PLATYPLATY_RENDERER_STATE_HPP
#define PLATYPLATY_RENDERER_STATE_HPP

#include <string>

namespace platyplaty {

enum class RendererPhase {
    WAITING_FOR_CONFIG,  // Before CHANGE AUDIO SOURCE
    WAITING_FOR_INIT,    // After CHANGE AUDIO SOURCE, before INIT
    RUNNING              // After successful INIT
};

struct RendererState {
    RendererPhase phase{RendererPhase::WAITING_FOR_CONFIG};
    std::string audio_source{};
};

}  // namespace platyplaty

#endif  // PLATYPLATY_RENDERER_STATE_HPP
