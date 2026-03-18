"""
System tray icon with toggle on/off and language selection.
Uses pystray to create a native Windows system tray icon.
"""

import threading
from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem as Item

from translator import TARGET_LANGUAGES, DEFAULT_TARGET


class TrayIcon:
    """System tray icon with Enable/Disable toggle and language selection."""

    def __init__(self, on_toggle=None, on_language_change=None, on_exit=None):
        """
        Args:
            on_toggle: callback(enabled: bool) when toggle is clicked
            on_language_change: callback(lang_code: str) when language changes
            on_exit: callback() when exit is clicked
        """
        self.on_toggle = on_toggle
        self.on_language_change = on_language_change
        self.on_exit = on_exit
        self._enabled = True
        self._target_lang = DEFAULT_TARGET
        self._icon = None
        self._thread = None

    @property
    def enabled(self):
        return self._enabled

    @property
    def target_lang(self):
        return self._target_lang

    def start(self):
        """Start the system tray icon in a background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the system tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _run(self):
        """Run the tray icon (blocking)."""
        self._icon = pystray.Icon(
            "winTranslate",
            icon=self._create_icon(self._enabled),
            title="winTranslate - Text Translator",
            menu=self._build_menu(),
        )
        self._icon.run()

    def _build_menu(self):
        """Build the context menu."""
        # Language submenu items
        lang_items = []
        for code, name in TARGET_LANGUAGES.items():
            lang_items.append(
                Item(
                    name,
                    self._make_lang_handler(code),
                    checked=lambda item, c=code: self._target_lang == c,
                    radio=True,
                )
            )

        menu = pystray.Menu(
            Item(
                "Enable",
                self._toggle_handler,
                checked=lambda item: self._enabled,
            ),
            pystray.Menu.SEPARATOR,
            Item("Target Language", pystray.Menu(*lang_items)),
            pystray.Menu.SEPARATOR,
            Item("Exit", self._exit_handler),
        )
        return menu

    def _make_lang_handler(self, lang_code):
        """Create a handler for language selection."""
        def handler(icon, item):
            self._target_lang = lang_code
            if self.on_language_change:
                self.on_language_change(lang_code)
            # Update menu
            icon.menu = self._build_menu()
            icon.update_menu()
        return handler

    def _toggle_handler(self, icon, item):
        """Handle Enable/Disable toggle."""
        self._enabled = not self._enabled
        icon.icon = self._create_icon(self._enabled)
        icon.title = (
            "winTranslate - Enabled" if self._enabled else "winTranslate - Disabled"
        )
        if self.on_toggle:
            self.on_toggle(self._enabled)

    def _exit_handler(self, icon, item):
        """Handle Exit."""
        if self.on_exit:
            self.on_exit()
        icon.stop()

    @staticmethod
    def _create_icon(enabled=True):
        """Create tray icon image (blue=enabled, gray=disabled)."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if enabled:
            # Blue circle with "T" for translate
            bg_color = (137, 180, 250, 255)  # #89b4fa
            text_color = (30, 30, 46, 255)   # #1e1e2e
        else:
            # Gray circle
            bg_color = (108, 112, 134, 255)  # #6c7086
            text_color = (30, 30, 46, 255)

        # Draw circle
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=bg_color,
        )

        # Draw "T" letter
        try:
            font = ImageFont.truetype("segoeui.ttf", 32)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except Exception:
                font = ImageFont.load_default()

        text = "T"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (size - tw) // 2
        ty = (size - th) // 2 - 2

        draw.text((tx, ty), text, fill=text_color, font=font)

        return img
