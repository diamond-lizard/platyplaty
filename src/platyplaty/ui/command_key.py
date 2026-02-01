#!/usr/bin/env python3
"""Key handling for the command prompt."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.ui.editing_mode import EditingMode
    from platyplaty.ui.prompt_interface import PromptInterface


from platyplaty.ui.editing_mode import PromptState


async def handle_prompt_control_key(
    key: str,
    prompt: "PromptInterface",
) -> bool | None:
    """Handle prompt-control keys (escape, ctrl+c, enter).

    These keys dismiss the prompt or execute commands. They are handled
    separately from text-editing keys to support different state management.

    Args:
        key: The key that was pressed.
        prompt: The CommandPrompt widget instance.

    Returns:
        True or False if the key was handled, None if it should be
        handled by text-editing logic.
    """
    if key in ("escape", "ctrl+c"):
        prompt.hide()
        return False
    if key == "enter":
        if prompt.input_text and prompt.callback:
            await prompt.callback(prompt.input_text)
        else:
            prompt.hide()
        prompt.cursor_index = 0
        return False
    return None

async def handle_command_key(
    key: str,
    prompt: "PromptInterface",
    character: str | None,
    editing_mode: "EditingMode",
) -> bool:
    """Handle a key press in the command prompt.

    Args:
        key: The key that was pressed.
        prompt: The CommandPrompt widget instance.
        character: The printable character, or None if not printable.
        editing_mode: The editing mode for emacs/vi keybindings.

    Returns:
        True if text or cursor position changed, False otherwise.
    """
    # Handle prompt-control keys (escape, ctrl+c, enter)
    control_result = await handle_prompt_control_key(key, prompt)
    if control_result is not None:
        return control_result

    # Delegate to editing mode for emacs/vi keybindings
    result = editing_mode.handle_key(
        key, character, PromptState(prompt.input_text, prompt.cursor_index)
    )
    if result is not None:
        prompt.input_text = result.new_text
        prompt.update_cursor_with_scroll(result.new_cursor)
        return result.state_changed

    # Text-editing keys: use single exit point pattern
    state_changed = False
    if key == "left":
        if prompt.cursor_index > 0:
            prompt.update_cursor_with_scroll(prompt.cursor_index - 1)
            state_changed = True
    elif key == "right":
        if prompt.cursor_index < len(prompt.input_text):
            prompt.update_cursor_with_scroll(prompt.cursor_index + 1)
            state_changed = True
    elif key == "home":
        if prompt.cursor_index > 0:
            prompt.update_cursor_with_scroll(0)
            state_changed = True
    elif key == "end":
        text_len = len(prompt.input_text)
        if prompt.cursor_index < text_len:
            prompt.update_cursor_with_scroll(text_len)
            state_changed = True
    elif key == "backspace":
        idx = prompt.cursor_index
        if idx > 0:
            prompt.input_text = prompt.input_text[:idx-1] + prompt.input_text[idx:]
            prompt.update_cursor_with_scroll(idx - 1)
            state_changed = True
    elif key == "delete":
        idx = prompt.cursor_index
        if idx < len(prompt.input_text):
            prompt.input_text = prompt.input_text[:idx] + prompt.input_text[idx+1:]
            state_changed = True
    elif key == "shift+insert":
        state_changed = prompt.paste_from_selection()
    elif character is not None and character.isprintable():
        idx = prompt.cursor_index
        text = prompt.input_text
        prompt.input_text = text[:idx] + character + text[idx:]
        prompt.update_cursor_with_scroll(idx + 1)
        state_changed = True
    editing_mode.reset_cut_chain()
    return state_changed

