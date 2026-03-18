"""
Floating popup UI for displaying translation results.
Shows a small "Translate" button near mouse cursor, expands to show translation.
"""

import tkinter as tk
import threading


class TranslatePopup:
    """Floating popup that shows translate button and translation results."""

    # Colors - Catppuccin Mocha theme
    BG_COLOR = "#1e1e2e"
    BG_SECONDARY = "#313244"
    TEXT_COLOR = "#cdd6f4"
    TEXT_SECONDARY = "#a6adc8"
    ACCENT_COLOR = "#89b4fa"
    ACCENT_HOVER = "#74c7ec"
    BORDER_COLOR = "#45475a"
    SUCCESS_COLOR = "#a6e3a1"
    ERROR_COLOR = "#f38ba8"

    def __init__(self, root, translate_callback=None, on_show=None, on_hide=None):
        """
        Args:
            root: Tkinter root window
            translate_callback: function(text) -> dict with 'translated', 'error' keys
            on_show: callback() when popup appears (to pause selection detector)
            on_hide: callback() when popup disappears (to resume selection detector)
        """
        self.root = root
        self.translate_callback = translate_callback
        self.on_show = on_show
        self.on_hide = on_hide
        self._popup = None
        self._selected_text = ""
        self._is_visible = False
        self._dismiss_timer = None

    def show(self, text, x, y):
        """Show the translate button near the given position."""
        self.root.after(0, lambda: self._show_impl(text, x, y))

    def hide(self):
        """Hide the popup."""
        self.root.after(0, self._hide_impl)

    def _show_impl(self, text, x, y):
        """Internal: create and show the popup window."""
        # Destroy existing popup
        self._hide_impl()

        self._selected_text = text
        self._is_visible = True

        # Notify that popup is visible (pause selection detector)
        if self.on_show:
            self.on_show()

        # Create popup window
        self._popup = tk.Toplevel(self.root)
        self._popup.withdraw()  # Hide while configuring
        self._popup.overrideredirect(True)
        self._popup.attributes("-topmost", True)
        self._popup.configure(bg=self.BORDER_COLOR)
        # Set transparency for the window
        self._popup.attributes("-alpha", 0.95)

        # Main frame with padding (creates border effect)
        main_frame = tk.Frame(self._popup, bg=self.BG_COLOR, padx=1, pady=1)
        main_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # Content frame
        self._content = tk.Frame(main_frame, bg=self.BG_COLOR, padx=10, pady=8)
        self._content.pack(fill="both", expand=True)

        # Preview of selected text (truncated)
        preview = text[:80] + "..." if len(text) > 80 else text
        preview = preview.replace("\n", " ")

        preview_label = tk.Label(
            self._content,
            text=f'"{preview}"',
            bg=self.BG_COLOR,
            fg=self.TEXT_SECONDARY,
            font=("Segoe UI", 9, "italic"),
            wraplength=350,
            justify="left",
            anchor="w",
        )
        preview_label.pack(fill="x", pady=(0, 6))

        # Button row
        btn_frame = tk.Frame(self._content, bg=self.BG_COLOR)
        btn_frame.pack(fill="x")

        # Translate button
        self._translate_btn = tk.Label(
            btn_frame,
            text="🌐 Translate",
            bg=self.ACCENT_COLOR,
            fg=self.BG_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=5,
            cursor="hand2",
        )
        self._translate_btn.pack(side="left")
        self._translate_btn.bind("<Button-1>", self._on_translate_click)
        self._translate_btn.bind(
            "<Enter>",
            lambda e: self._translate_btn.configure(bg=self.ACCENT_HOVER),
        )
        self._translate_btn.bind(
            "<Leave>",
            lambda e: self._translate_btn.configure(bg=self.ACCENT_COLOR),
        )

        # Close button
        close_btn = tk.Label(
            btn_frame,
            text="✕",
            bg=self.BG_COLOR,
            fg=self.TEXT_SECONDARY,
            font=("Segoe UI", 11),
            padx=8,
            pady=5,
            cursor="hand2",
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self._hide_impl())
        close_btn.bind(
            "<Enter>", lambda e: close_btn.configure(fg=self.ERROR_COLOR)
        )
        close_btn.bind(
            "<Leave>", lambda e: close_btn.configure(fg=self.TEXT_SECONDARY)
        )

        # Result area placeholder
        self._result_frame = tk.Frame(self._content, bg=self.BG_COLOR)

        # Position popup near mouse, ensuring it stays on screen
        self._popup.update_idletasks()
        popup_w = self._popup.winfo_reqwidth()
        popup_h = self._popup.winfo_reqheight()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # Position: below and to the right of cursor
        px = x + 10
        py = y + 15

        # Adjust if going off screen
        if px + popup_w > screen_w:
            px = x - popup_w - 10
        if py + popup_h + 100 > screen_h:  # Extra space for translation result
            py = y - popup_h - 15
        if px < 0:
            px = 5
        if py < 0:
            py = 5

        self._popup.geometry(f"+{px}+{py}")
        self._popup.deiconify()

        # Start auto-dismiss timer - check periodically if user clicked outside
        self._start_dismiss_check()

    def _start_dismiss_check(self):
        """Periodically check if user clicked outside popup to dismiss it."""
        # We use a simple approach: bind mouse click globally via root
        # and check if the click was inside or outside our popup
        self._popup.bind("<Button-1>", self._on_popup_click)
        # We'll use periodic polling since FocusOut doesn't work with overrideredirect
        self._schedule_focus_check()

    def _on_popup_click(self, event):
        """Resets the dismiss timer when clicking inside popup."""
        # Click was inside popup, do nothing (keep it alive)
        pass

    def _schedule_focus_check(self):
        """Schedule periodic check - auto dismiss after 30 seconds of inactivity."""
        if not self._popup or not self._is_visible:
            return
        # Re-check in 30 seconds
        self._dismiss_timer = self.root.after(30000, self._hide_impl)

    def _hide_impl(self):
        """Internal: destroy the popup window."""
        # Cancel dismiss timer
        if self._dismiss_timer:
            try:
                self.root.after_cancel(self._dismiss_timer)
            except Exception:
                pass
            self._dismiss_timer = None

        if self._popup:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None

        was_visible = self._is_visible
        self._is_visible = False

        # Notify that popup is hidden (resume selection detector)
        if was_visible and self.on_hide:
            # Small delay before resuming detection to avoid capturing the dismiss click
            self.root.after(300, self.on_hide)

    def _on_translate_click(self, event=None):
        """Handle translate button click."""
        if not self.translate_callback or not self._selected_text:
            return

        # Show loading state
        self._translate_btn.configure(
            text="⏳ Translating...",
            bg=self.BG_SECONDARY,
            fg=self.TEXT_SECONDARY,
        )
        self._translate_btn.unbind("<Button-1>")

        # Run translation in background
        threading.Thread(
            target=self._do_translate, daemon=True
        ).start()

    def _do_translate(self):
        """Perform translation in background thread."""
        result = self.translate_callback(self._selected_text)
        # Update UI on main thread
        self.root.after(0, lambda: self._show_result(result))

    def _show_result(self, result):
        """Display translation result in the popup."""
        if not self._popup or not self._is_visible:
            return

        try:
            # Update button to allow re-translate
            self._translate_btn.configure(
                text="🌐 Translate",
                bg=self.ACCENT_COLOR,
                fg=self.BG_COLOR,
            )
            self._translate_btn.bind("<Button-1>", self._on_translate_click)
        except Exception:
            return

        # Clear previous result
        for widget in self._result_frame.winfo_children():
            widget.destroy()

        self._result_frame.pack(fill="x", pady=(8, 0))

        # Separator
        sep = tk.Frame(self._result_frame, bg=self.BORDER_COLOR, height=1)
        sep.pack(fill="x", pady=(0, 6))

        if result.get("error"):
            # Error message
            error_label = tk.Label(
                self._result_frame,
                text=f"❌ {result['error']}",
                bg=self.BG_COLOR,
                fg=self.ERROR_COLOR,
                font=("Segoe UI", 9),
                wraplength=350,
                justify="left",
                anchor="w",
            )
            error_label.pack(fill="x")
        else:
            # Translation result
            translated_text = result.get("translated", "")

            result_label = tk.Label(
                self._result_frame,
                text=translated_text,
                bg=self.BG_SECONDARY,
                fg=self.TEXT_COLOR,
                font=("Segoe UI", 10),
                wraplength=350,
                justify="left",
                anchor="w",
                padx=10,
                pady=8,
            )
            result_label.pack(fill="x")

            # Copy button
            copy_frame = tk.Frame(self._result_frame, bg=self.BG_COLOR)
            copy_frame.pack(fill="x", pady=(4, 0))

            copy_btn = tk.Label(
                copy_frame,
                text="📋 Copy",
                bg=self.BG_SECONDARY,
                fg=self.TEXT_SECONDARY,
                font=("Segoe UI", 9),
                padx=8,
                pady=3,
                cursor="hand2",
            )
            copy_btn.pack(side="left")
            copy_btn.bind(
                "<Button-1>",
                lambda e: self._copy_result(translated_text, copy_btn),
            )
            copy_btn.bind(
                "<Enter>",
                lambda e: copy_btn.configure(fg=self.TEXT_COLOR),
            )
            copy_btn.bind(
                "<Leave>",
                lambda e: copy_btn.configure(fg=self.TEXT_SECONDARY),
            )

        # Reposition to stay on screen
        try:
            self._popup.update_idletasks()
            popup_w = self._popup.winfo_reqwidth()
            popup_h = self._popup.winfo_reqheight()
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()

            curr_x = self._popup.winfo_x()
            curr_y = self._popup.winfo_y()

            if curr_x + popup_w > screen_w:
                curr_x = screen_w - popup_w - 5
            if curr_y + popup_h > screen_h:
                curr_y = screen_h - popup_h - 5

            self._popup.geometry(f"+{curr_x}+{curr_y}")
        except Exception:
            pass

    def _copy_result(self, text, btn):
        """Copy translation result to clipboard."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            btn.configure(text="✅ Copied!", fg=self.SUCCESS_COLOR)
            self.root.after(
                1500,
                lambda: self._safe_configure(btn, text="📋 Copy", fg=self.TEXT_SECONDARY),
            )
        except Exception:
            pass

    def _safe_configure(self, widget, **kwargs):
        """Safely configure a widget (may have been destroyed)."""
        try:
            widget.configure(**kwargs)
        except Exception:
            pass
