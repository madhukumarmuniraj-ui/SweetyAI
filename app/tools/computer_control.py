"""
SweetyAI Advanced Computer Control Tools
PyAutoGUI mouse/keyboard control, window management, clipboard history, hotkeys.

All third-party dependencies are optional: every function reports a clean
error string (or safe default) when its backing library is unavailable.
"""

import os
import sys
import time
from typing import Tuple, List, Optional, Dict, Any
import json

# -----------------------------------------------------------------------------
# OPTIONAL DEPENDENCY LOADING (each guarded independently)
# -----------------------------------------------------------------------------

try:
    # python-xlib warns "no xauthority details available" when ~/.Xauthority
    # has no entry for the display; harmless, but noisy at import time.
    import logging as _logging
    _logging.getLogger("Xlib.xauth").setLevel(_logging.ERROR)

    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # Safety settings
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except Exception:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False
    print("[Computer Control] PyAutoGUI not available. Run: pip install pyautogui")

try:
    import pygetwindow as gw
    WINDOW_CONTROL_AVAILABLE = True
except Exception:
    gw = None
    WINDOW_CONTROL_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except Exception:
    keyboard = None
    KEYBOARD_AVAILABLE = False
    print("[Computer Control] keyboard not available. Run: pip install keyboard")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except Exception:
    pyperclip = None
    PYPERCLIP_AVAILABLE = False


# =============================================================================
# MOUSE CONTROL
# =============================================================================

def move_mouse(x: int, y: int, duration: float = 0.2) -> str:
    """Move mouse to specified coordinates."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return f"Mouse moved to ({x}, {y})"
    except Exception as e:
        return f"Error moving mouse: {e}"


def click_mouse(x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1) -> str:
    """Click mouse at current position or specified coordinates."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
            return f"Clicked {button} button {clicks} time(s) at ({x}, {y})"
        else:
            pyautogui.click(clicks=clicks, button=button)
            return f"Clicked {button} button {clicks} time(s)"
    except Exception as e:
        return f"Error clicking mouse: {e}"


def double_click(x: Optional[int] = None, y: Optional[int] = None) -> str:
    """Double-click mouse."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
        return "Double-clicked"
    except Exception as e:
        return f"Error double-clicking: {e}"


def right_click(x: Optional[int] = None, y: Optional[int] = None) -> str:
    """Right-click mouse."""
    return click_mouse(x, y, button='right', clicks=1)


def drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> str:
    """Drag mouse from start to end position."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
        return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
    except Exception as e:
        return f"Error dragging mouse: {e}"


def scroll_mouse(clicks: int, direction: str = 'down') -> str:
    """Scroll mouse wheel."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        scroll_amount = -clicks if direction == 'down' else clicks
        pyautogui.scroll(scroll_amount)
        return f"Scrolled {direction} {abs(clicks)} clicks"
    except Exception as e:
        return f"Error scrolling: {e}"


def get_mouse_position() -> Tuple[int, int]:
    """Get current mouse position."""
    if not PYAUTOGUI_AVAILABLE:
        return (0, 0)
    try:
        return pyautogui.position()
    except Exception:
        return (0, 0)


def get_screen_size() -> Tuple[int, int]:
    """Get screen resolution."""
    if not PYAUTOGUI_AVAILABLE:
        return (0, 0)
    try:
        return pyautogui.size()
    except Exception:
        return (0, 0)


# =============================================================================
# KEYBOARD CONTROL
# =============================================================================

def type_text(text: str, interval: float = 0.01) -> str:
    """Type text using keyboard."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed: {text[:50]}..."
    except Exception as e:
        return f"Error typing text: {e}"


def press_key(key: str) -> str:
    """Press a single key."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Error pressing key: {e}"


def press_hotkey(*keys: str) -> str:
    """Press a combination of keys (e.g., 'ctrl', 'c')."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey: {' + '.join(keys)}"
    except Exception as e:
        return f"Error pressing hotkey: {e}"


def hold_key(key: str, duration: float = 1.0) -> str:
    """Hold a key for specified duration."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        return f"Held key {key} for {duration}s"
    except Exception as e:
        return f"Error holding key: {e}"


# =============================================================================
# WINDOW MANAGEMENT
# =============================================================================

def list_windows() -> List[str]:
    """Get list of all open windows."""
    if not WINDOW_CONTROL_AVAILABLE:
        return ["Error: pygetwindow not available"]
    try:
        windows = gw.getAllTitles()
        return [w for w in windows if w]  # Filter empty titles
    except Exception as e:
        return [f"Error: {e}"]


def get_active_window() -> str:
    """Get title of active window."""
    if not WINDOW_CONTROL_AVAILABLE:
        return "Error: pygetwindow not available"
    try:
        window = gw.getActiveWindow()
        return window.title if window else "No active window"
    except Exception as e:
        return f"Error: {e}"


def activate_window(title: str) -> str:
    """Bring window to foreground by title (partial match)."""
    if not WINDOW_CONTROL_AVAILABLE:
        return "Error: pygetwindow not available"
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].activate()
            return f"Activated window: {windows[0].title}"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Error activating window: {e}"


def minimize_window(title: str) -> str:
    """Minimize window by title."""
    if not WINDOW_CONTROL_AVAILABLE:
        return "Error: pygetwindow not available"
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].minimize()
            return f"Minimized window: {windows[0].title}"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Error minimizing window: {e}"


def maximize_window(title: str) -> str:
    """Maximize window by title."""
    if not WINDOW_CONTROL_AVAILABLE:
        return "Error: pygetwindow not available"
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].maximize()
            return f"Maximized window: {windows[0].title}"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Error maximizing window: {e}"


def resize_window(title: str, width: int, height: int) -> str:
    """Resize window by title."""
    if not WINDOW_CONTROL_AVAILABLE:
        return "Error: pygetwindow not available"
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].resizeTo(width, height)
            return f"Resized window to {width}x{height}"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Error resizing window: {e}"


def move_window(title: str, x: int, y: int) -> str:
    """Move window to specified position."""
    if not WINDOW_CONTROL_AVAILABLE:
        return "Error: pygetwindow not available"
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].moveTo(x, y)
            return f"Moved window to ({x}, {y})"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Error moving window: {e}"


def close_window(title: str) -> str:
    """Close window by title."""
    if not WINDOW_CONTROL_AVAILABLE:
        return "Error: pygetwindow not available"
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].close()
            return f"Closed window: {windows[0].title}"
        return f"No window found with title: {title}"
    except Exception as e:
        return f"Error closing window: {e}"


# =============================================================================
# SCREEN CAPTURE
# =============================================================================

def screenshot_region(x: int, y: int, width: int, height: int, save_path: str) -> str:
    """Take screenshot of specific screen region."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save(save_path)
        return f"Screenshot saved: {save_path}"
    except Exception as e:
        return f"Error taking screenshot: {e}"


def find_image_on_screen(image_path: str, confidence: float = 0.9) -> Optional[Tuple[int, int]]:
    """Find image on screen and return its position."""
    if not PYAUTOGUI_AVAILABLE:
        return None
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            return pyautogui.center(location)
        return None
    except Exception:
        return None


def click_on_image(image_path: str, confidence: float = 0.9) -> str:
    """Find and click on an image on screen."""
    if not PYAUTOGUI_AVAILABLE:
        return "Error: PyAutoGUI not installed"
    try:
        location = find_image_on_screen(image_path, confidence)
        if location:
            pyautogui.click(location)
            return f"Clicked on image at {location}"
        return "Image not found on screen"
    except Exception as e:
        return f"Error clicking on image: {e}"


# =============================================================================
# CLIPBOARD HISTORY (Simple Implementation)
# =============================================================================

_clipboard_history = []
_max_history = 50


def save_to_clipboard_history(text: str):
    """Save text to clipboard history."""
    global _clipboard_history
    if text and text not in _clipboard_history:
        _clipboard_history.insert(0, text)
        if len(_clipboard_history) > _max_history:
            _clipboard_history = _clipboard_history[:_max_history]


def get_clipboard_history() -> List[str]:
    """Get clipboard history."""
    return _clipboard_history.copy()


def clear_clipboard_history() -> str:
    """Clear clipboard history."""
    global _clipboard_history
    _clipboard_history = []
    return "Clipboard history cleared"


# =============================================================================
# HOTKEY REGISTRATION (Requires keyboard library)
# =============================================================================

_registered_hotkeys = {}


def register_hotkey(hotkey: str, callback_name: str) -> str:
    """Register a global hotkey (requires keyboard library with admin privileges)."""
    if not KEYBOARD_AVAILABLE:
        return "Error: keyboard library not available"
    try:
        # Note: This requires admin privileges on Windows
        keyboard.add_hotkey(hotkey, lambda: print(f"Hotkey {hotkey} triggered: {callback_name}"))
        _registered_hotkeys[hotkey] = callback_name
        return f"Hotkey registered: {hotkey}"
    except Exception as e:
        return f"Error registering hotkey (may need admin privileges): {e}"


def unregister_hotkey(hotkey: str) -> str:
    """Unregister a global hotkey."""
    if not KEYBOARD_AVAILABLE:
        return "Error: keyboard library not available"
    try:
        keyboard.remove_hotkey(hotkey)
        if hotkey in _registered_hotkeys:
            del _registered_hotkeys[hotkey]
        return f"Hotkey unregistered: {hotkey}"
    except Exception as e:
        return f"Error unregistering hotkey: {e}"


def list_registered_hotkeys() -> List[str]:
    """Get list of registered hotkeys."""
    return list(_registered_hotkeys.keys())


# =============================================================================
# AUTOMATION MACROS
# =============================================================================

def record_macro(duration: int = 10) -> List[Dict[str, Any]]:
    """Record mouse and keyboard events for specified duration (requires keyboard library)."""
    if not KEYBOARD_AVAILABLE:
        return [{"error": "keyboard library not available"}]
    try:
        events = []
        start_time = time.time()

        def on_event(event):
            if time.time() - start_time < duration:
                events.append({
                    'time': time.time() - start_time,
                    'type': 'keyboard',
                    'name': event.name,
                    'event_type': event.event_type
                })

        keyboard.hook(on_event)
        time.sleep(duration)
        keyboard.unhook_all()

        return events
    except Exception as e:
        return [{"error": str(e)}]


# =============================================================================
# CLIPBOARD HELPERS (uses pyperclip when available)
# =============================================================================

def copy_to_clipboard(text: str) -> str:
    """Copy text to the system clipboard."""
    if not PYPERCLIP_AVAILABLE:
        return "Error: pyperclip not installed"
    try:
        pyperclip.copy(text)
        save_to_clipboard_history(text)
        return "Copied to clipboard"
    except Exception as e:
        return f"Error copying to clipboard: {e}"


def paste_from_clipboard() -> str:
    """Read text from the system clipboard."""
    if not PYPERCLIP_AVAILABLE:
        return "Error: pyperclip not installed"
    try:
        text = pyperclip.paste()
        save_to_clipboard_history(text)
        return text
    except Exception as e:
        return f"Error reading clipboard: {e}"


__all__ = [
    # Mouse
    'move_mouse', 'click_mouse', 'double_click', 'right_click',
    'drag_mouse', 'scroll_mouse', 'get_mouse_position', 'get_screen_size',
    # Keyboard
    'type_text', 'press_key', 'press_hotkey', 'hold_key',
    # Window Management
    'list_windows', 'get_active_window', 'activate_window',
    'minimize_window', 'maximize_window', 'resize_window',
    'move_window', 'close_window',
    # Screen
    'screenshot_region', 'find_image_on_screen', 'click_on_image',
    # Clipboard
    'save_to_clipboard_history', 'get_clipboard_history', 'clear_clipboard_history',
    'copy_to_clipboard', 'paste_from_clipboard',
    # Hotkeys
    'register_hotkey', 'unregister_hotkey', 'list_registered_hotkeys',
    # Macros
    'record_macro'
]
