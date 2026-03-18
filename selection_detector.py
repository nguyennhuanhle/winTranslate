"""
System-wide text selection detector.
Monitors mouse events to detect text selection, then reads clipboard.
"""

import time
import threading

import pyperclip
from pynput import mouse, keyboard


# Minimum drag distance (pixels) to consider as text selection
MIN_DRAG_DISTANCE = 15
# Debounce time (seconds) between selection detections
DEBOUNCE_TIME = 0.8


class SelectionDetector:
    """Detects text selection in any Windows application."""

    def __init__(self, on_text_selected=None):
        """
        Args:
            on_text_selected: callback(text, x, y) called when text is selected.
                              x, y = mouse position at release.
        """
        self.on_text_selected = on_text_selected
        self._enabled = True
        self._paused = False  # Temporarily pause (e.g. while popup is visible)
        self._mouse_listener = None
        self._kb_controller = keyboard.Controller()
        self._press_pos = None
        self._last_trigger_time = 0
        self._lock = threading.Lock()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, value):
        self._paused = value

    def start(self):
        """Start listening for mouse events."""
        self._mouse_listener = mouse.Listener(
            on_click=self._on_click,
        )
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

    def stop(self):
        """Stop listening for mouse events."""
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

    def _on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not self._enabled or self._paused:
            return
        if button != mouse.Button.left:
            return

        if pressed:
            # Mouse button pressed - record position
            self._press_pos = (x, y)
        else:
            # Mouse button released - check if it was a drag (text selection)
            if self._press_pos is None:
                return

            dx = abs(x - self._press_pos[0])
            dy = abs(y - self._press_pos[1])
            drag_distance = (dx ** 2 + dy ** 2) ** 0.5

            self._press_pos = None

            # Check minimum drag distance
            if drag_distance < MIN_DRAG_DISTANCE:
                return

            # Debounce
            now = time.time()
            if now - self._last_trigger_time < DEBOUNCE_TIME:
                return
            self._last_trigger_time = now

            # Try to get selected text via clipboard
            threading.Thread(
                target=self._try_get_selection, args=(x, y), daemon=True
            ).start()

    def _try_get_selection(self, x, y):
        """Try to get selected text by simulating Ctrl+C and reading clipboard."""
        if not self._lock.acquire(blocking=False):
            return  # Another detection is in progress
        try:
            # Backup current clipboard
            try:
                old_clipboard = pyperclip.paste()
            except Exception:
                old_clipboard = ""

            # Clear clipboard to detect new content
            try:
                pyperclip.copy("")
            except Exception:
                pass

            # Small delay to ensure mouse release is processed
            time.sleep(0.05)

            # Simulate Ctrl+C using pynput keyboard controller
            try:
                with self._kb_controller.pressed(keyboard.Key.ctrl):
                    self._kb_controller.tap('c')
            except Exception as e:
                print(f"Ctrl+C simulation error: {e}")
                # Restore clipboard
                if old_clipboard:
                    try:
                        pyperclip.copy(old_clipboard)
                    except Exception:
                        pass
                return

            # Wait for clipboard to update
            time.sleep(0.2)

            # Read clipboard
            try:
                new_text = pyperclip.paste()
            except Exception:
                new_text = ""

            # Restore original clipboard
            try:
                if old_clipboard:
                    pyperclip.copy(old_clipboard)
                else:
                    pyperclip.copy("")
            except Exception:
                pass

            # Check if we got new text
            if new_text and new_text.strip():
                if self.on_text_selected:
                    self.on_text_selected(new_text.strip(), x, y)

        except Exception as e:
            print(f"Selection detection error: {e}")
        finally:
            self._lock.release()
