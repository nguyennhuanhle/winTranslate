"""
winTranslate - Windows System-wide Text Translation App

Select text in any application → click Translate → see translation.
Toggle on/off via system tray icon.
"""

import tkinter as tk

from translator import translate_text, DEFAULT_TARGET
from selection_detector import SelectionDetector
from popup_ui import TranslatePopup
from tray_icon import TrayIcon


class WinTranslateApp:
    """Main application that connects all components."""

    def __init__(self):
        # Target language
        self._target_lang = DEFAULT_TARGET

        # Create hidden Tkinter root
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("winTranslate")

        # Create popup with show/hide callbacks to pause/resume detector
        self.popup = TranslatePopup(
            root=self.root,
            translate_callback=self._translate,
            on_show=self._on_popup_show,
            on_hide=self._on_popup_hide,
        )

        # Create selection detector
        self.detector = SelectionDetector(
            on_text_selected=self._on_text_selected,
        )

        # Create tray icon
        self.tray = TrayIcon(
            on_toggle=self._on_toggle,
            on_language_change=self._on_language_change,
            on_exit=self._on_exit,
        )

    def run(self):
        """Start the application."""
        print("winTranslate starting...")
        print(f"Target language: {self._target_lang}")
        print("Select text in any application and a translate popup will appear.")
        print("Right-click the tray icon to toggle or change settings.")

        # Start selection detector
        self.detector.start()
        print("[OK] Selection detector started")

        # Start tray icon
        self.tray.start()
        print("[OK] Tray icon started")

        # Run Tkinter main loop (for popup UI)
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_exit()

    def _on_text_selected(self, text, x, y):
        """Called when text is selected in any application."""
        print(f"[SELECTED] ({len(text)} chars) at ({x}, {y}): {text[:50]}...")
        # Show popup near cursor
        self.popup.show(text, x, y)

    def _on_popup_show(self):
        """Called when popup appears - pause selection detection."""
        self.detector.paused = True

    def _on_popup_hide(self):
        """Called when popup disappears - resume selection detection."""
        self.detector.paused = False

    def _translate(self, text):
        """Translate text using current target language."""
        print(f"[TRANSLATE] {text[:50]}... → {self._target_lang}")
        result = translate_text(text, target_lang=self._target_lang)
        if result.get("error"):
            print(f"[ERROR] {result['error']}")
        else:
            print(f"[RESULT] {result['translated'][:50]}...")
        return result

    def _on_toggle(self, enabled):
        """Called when Enable/Disable is toggled in tray."""
        self.detector.enabled = enabled
        if not enabled:
            self.popup.hide()
        status = "ENABLED" if enabled else "DISABLED"
        print(f"[TOGGLE] winTranslate {status}")

    def _on_language_change(self, lang_code):
        """Called when target language changes in tray."""
        self._target_lang = lang_code
        print(f"[LANG] Target language changed to: {lang_code}")

    def _on_exit(self):
        """Called when Exit is clicked in tray."""
        print("winTranslate exiting...")
        self.detector.stop()
        self.tray.stop()
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass


def main():
    app = WinTranslateApp()
    app.run()


if __name__ == "__main__":
    main()
