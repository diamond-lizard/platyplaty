// Scancode to key name mapping.
// Translates SDL scancodes to prompt_toolkit-style key names.

#ifndef PLATYPLATY_SCANCODE_MAP_HPP
#define PLATYPLATY_SCANCODE_MAP_HPP

#include <SDL2/SDL_scancode.h>
#include <optional>
#include <string>

namespace platyplaty {

// Translate an SDL scancode and modifier state to a key name.
// Returns the key name in prompt_toolkit-style format (lowercase,
// with optional control-/shift-/alt- prefixes for modifiers).
// Returns std::nullopt for unmapped scancodes.
std::optional<std::string> scancode_to_keyname(
    SDL_Scancode scancode,
    bool ctrl,
    bool shift,
    bool alt);

}  // namespace platyplaty

#endif  // PLATYPLATY_SCANCODE_MAP_HPP
