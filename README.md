# winTranslate

> System-wide text translation for Windows — select text anywhere, get instant translation.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🌐 **Instant Translation** — Select (highlight) text in any application → popup appears → click Translate
- 🔍 **Auto-detect Language** — Supports English, Chinese, Japanese, Korean, French, German, Spanish, Thai, Russian, and more
- 🎯 **Multiple Target Languages** — Vietnamese (default), English, 中文, 日本語, 한국어, Français, Deutsch, Español, ภาษาไทย, Русский
- 🔄 **Toggle On/Off** — Enable or disable via system tray without affecting other Windows functions
- 📋 **Copy Result** — One-click copy translation to clipboard
- 🎨 **Dark Theme UI** — Clean, modern popup with Catppuccin Mocha colors

## 📦 Installation

### Option 1: Download Executable (Recommended)
Download `winTranslate.exe` from [Releases](../../releases) — no Python needed.

### Option 2: Run from Source
```bash
git clone https://github.com/YOUR_USERNAME/winTranslate.git
cd winTranslate
uv venv
uv pip install -r requirements.txt
.venv\Scripts\python main.py
```

## 🚀 Usage

1. **Run** `winTranslate.exe` or `python main.py`
2. **Look for** the blue "T" icon in the system tray
3. **Select text** (drag to highlight) in any application
4. **Click "🌐 Translate"** in the popup that appears near your cursor
5. **View** the translation result and optionally **copy** it

### System Tray Options (Right-click the "T" icon)
- **Enable / Disable** — Toggle text selection monitoring
- **Target Language** — Choose your preferred translation language
- **Exit** — Quit the application

## 🛠️ Build from Source

```bash
# Install dependencies
uv pip install -r requirements.txt
uv pip install pyinstaller

# Generate icon
.venv\Scripts\python create_icon.py

# Build exe
.venv\Scripts\pyinstaller --onefile --windowed --name winTranslate --icon app.ico --add-data "app.ico;." main.py
```

Output: `dist/winTranslate.exe`

## 📁 Project Structure

```
winTranslate/
├── main.py              # Entry point
├── translator.py        # Translation engine (Google Translate, auto-detect)
├── selection_detector.py # System-wide text selection detection
├── popup_ui.py          # Floating popup UI (Tkinter, dark theme)
├── tray_icon.py         # System tray icon with toggle & settings
├── create_icon.py       # Icon generator for the executable
├── requirements.txt     # Python dependencies
└── run.bat              # Quick-launch script
```

## ⚙️ How It Works

1. **Mouse Monitoring** — Uses `pynput` to detect drag-select gestures (mouse press → drag → release)
2. **Clipboard Capture** — Simulates `Ctrl+C` to copy selected text, reads clipboard, then restores original clipboard content
3. **Translation** — Sends text to Google Translate via `deep-translator` (auto-detects source language)
4. **Popup Display** — Shows a Tkinter floating window near the cursor with the translation result

## 📋 Requirements

- Windows 10/11
- Internet connection (uses Google Translate API)
- Python 3.10+ (only if running from source)

## 📄 License

MIT License
