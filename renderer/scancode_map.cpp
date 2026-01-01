// Scancode to key name mapping implementation.
// Translates SDL scancodes to prompt_toolkit-style key names.

#include "scancode_map.hpp"
#include <unordered_map>

namespace platyplaty {

namespace {

// Map of SDL scancodes to their base key names (without modifiers).
// Uses prompt_toolkit-style naming: lowercase letters, named keys.
const std::unordered_map<SDL_Scancode, std::string> g_scancode_map = {
    // Letter keys (a-z)
    {SDL_SCANCODE_A, "a"},
    {SDL_SCANCODE_B, "b"},
    {SDL_SCANCODE_C, "c"},
    {SDL_SCANCODE_D, "d"},
    {SDL_SCANCODE_E, "e"},
    {SDL_SCANCODE_F, "f"},
    {SDL_SCANCODE_G, "g"},
    {SDL_SCANCODE_H, "h"},
    {SDL_SCANCODE_I, "i"},
    {SDL_SCANCODE_J, "j"},
    {SDL_SCANCODE_K, "k"},
    {SDL_SCANCODE_L, "l"},
    {SDL_SCANCODE_M, "m"},
    {SDL_SCANCODE_N, "n"},
    {SDL_SCANCODE_O, "o"},
    {SDL_SCANCODE_P, "p"},
    {SDL_SCANCODE_Q, "q"},
    {SDL_SCANCODE_R, "r"},
    {SDL_SCANCODE_S, "s"},
    {SDL_SCANCODE_T, "t"},
    {SDL_SCANCODE_U, "u"},
    {SDL_SCANCODE_V, "v"},
    {SDL_SCANCODE_W, "w"},
    {SDL_SCANCODE_X, "x"},
    {SDL_SCANCODE_Y, "y"},
    {SDL_SCANCODE_Z, "z"},

    // Number keys (0-9)
    {SDL_SCANCODE_0, "0"},
    {SDL_SCANCODE_1, "1"},
    {SDL_SCANCODE_2, "2"},
    {SDL_SCANCODE_3, "3"},
    {SDL_SCANCODE_4, "4"},
    {SDL_SCANCODE_5, "5"},
    {SDL_SCANCODE_6, "6"},
    {SDL_SCANCODE_7, "7"},
    {SDL_SCANCODE_8, "8"},
    {SDL_SCANCODE_9, "9"},

    // Navigation keys
    {SDL_SCANCODE_UP, "up"},
    {SDL_SCANCODE_DOWN, "down"},
    {SDL_SCANCODE_LEFT, "left"},
    {SDL_SCANCODE_RIGHT, "right"},
    {SDL_SCANCODE_HOME, "home"},
    {SDL_SCANCODE_END, "end"},
    {SDL_SCANCODE_PAGEUP, "pageup"},
    {SDL_SCANCODE_PAGEDOWN, "pagedown"},
    {SDL_SCANCODE_INSERT, "insert"},
    {SDL_SCANCODE_DELETE, "delete"},

    // Function keys (f1-f24)
    {SDL_SCANCODE_F1, "f1"},
    {SDL_SCANCODE_F2, "f2"},
    {SDL_SCANCODE_F3, "f3"},
    {SDL_SCANCODE_F4, "f4"},
    {SDL_SCANCODE_F5, "f5"},
    {SDL_SCANCODE_F6, "f6"},
    {SDL_SCANCODE_F7, "f7"},
    {SDL_SCANCODE_F8, "f8"},
    {SDL_SCANCODE_F9, "f9"},
    {SDL_SCANCODE_F10, "f10"},
    {SDL_SCANCODE_F11, "f11"},
    {SDL_SCANCODE_F12, "f12"},
    {SDL_SCANCODE_F13, "f13"},
    {SDL_SCANCODE_F14, "f14"},
    {SDL_SCANCODE_F15, "f15"},
    {SDL_SCANCODE_F16, "f16"},
    {SDL_SCANCODE_F17, "f17"},
    {SDL_SCANCODE_F18, "f18"},
    {SDL_SCANCODE_F19, "f19"},
    {SDL_SCANCODE_F20, "f20"},
    {SDL_SCANCODE_F21, "f21"},
    {SDL_SCANCODE_F22, "f22"},
    {SDL_SCANCODE_F23, "f23"},
    {SDL_SCANCODE_F24, "f24"},

    // Special keys
    {SDL_SCANCODE_ESCAPE, "escape"},
    {SDL_SCANCODE_RETURN, "enter"},
    {SDL_SCANCODE_TAB, "tab"},
    {SDL_SCANCODE_BACKSPACE, "backspace"},
    {SDL_SCANCODE_SPACE, "space"},

    // Media keys
    {SDL_SCANCODE_AUDIOPLAY, "audioplay"},
    {SDL_SCANCODE_AUDIOPREV, "audioprev"},
    {SDL_SCANCODE_AUDIONEXT, "audionext"},
    {SDL_SCANCODE_AUDIOSTOP, "audiostop"},
    {SDL_SCANCODE_AUDIOMUTE, "audiomute"},
    {SDL_SCANCODE_VOLUMEUP, "volumeup"},
    {SDL_SCANCODE_VOLUMEDOWN, "volumedown"},
};

}  // namespace

std::optional<std::string> scancode_to_keyname(
    SDL_Scancode scancode,
    bool ctrl,
    bool shift,
    bool alt) {

    auto it = g_scancode_map.find(scancode);
    if (it == g_scancode_map.end()) {
        return std::nullopt;
    }

    std::string result;

    // Add modifier prefixes in consistent order: control-, shift-, alt-
    if (ctrl) {
        result += "control-";
    }
    if (shift) {
        result += "shift-";
    }
    if (alt) {
        result += "alt-";
    }

    result += it->second;
    return result;
}

}  // namespace platyplaty
