# winTranslate

> 🇬🇧 System-wide text translation — select text anywhere, get instant translation.
> 
> 🇻🇳 Dịch văn bản toàn hệ thống — bôi đen chữ ở bất kỳ đâu, dịch ngay lập tức.

![Tauri](https://img.shields.io/badge/Tauri-v2-blue?logo=tauri)
![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange?logo=rust)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-0078D6)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📥 Download / Tải về

| Version | Platform | Download |
|---------|----------|----------|
| **v2.0 (Tauri)** ⭐ | Windows x64 | [winTranslate_2.0.0_x64-setup.exe](../../releases) |
| v1.0 (Python) | Windows | [winTranslate.exe](../../releases/tag/v1.0) |

> **Recommended / Khuyên dùng:** Tauri v2 — nhẹ hơn (4 MB vs 22 MB), nhanh hơn, UI đẹp hơn.

---

## ✨ Features / Tính năng

- ⌨️ **Hotkey / Phím tắt** — `Ctrl+Shift+T` (Win) / `Cmd+Shift+T` (Mac) — auto-copy & translate / tự copy và dịch
- 🌐 **Auto-detect / Tự nhận diện** — Source language auto-detected / Tự nhận diện ngôn ngữ nguồn
- 🎯 **11 Languages / 11 Ngôn ngữ** — Vietnamese, English, 中文, 日本語, 한국어, Français, Deutsch, Español, ภาษาไทย, Русский, 中文繁體
- 🔄 **Toggle / Bật/Tắt** — System tray enable/disable / Bật tắt qua khay hệ thống
- 📋 **Copy** — One-click copy translation / Bấm 1 lần để copy bản dịch
- 🎨 **Dark Theme** — Catppuccin Mocha color scheme / Giao diện tối hiện đại
- 📖 **Built-in Help / Hướng dẫn tích hợp** — Bilingual guide / Song ngữ Anh-Việt

---

## 🚀 Usage / Cách sử dụng

1. **Run / Chạy** — Launch app → icon appears in system tray / Chạy app → icon xuất hiện ở khay hệ thống
2. **Select text / Bôi đen chữ** — In any app / Ở bất kỳ ứng dụng nào
3. **Press / Nhấn** `Ctrl+Shift+T` — Popup appears with translation / Popup hiện ra với bản dịch
4. **Copy / Sao chép** — Click Copy button / Bấm nút Copy
5. **Close / Đóng** — Click ✕ or press `Esc` / Bấm ✕ hoặc nhấn `Esc`

### System Tray / Khay hệ thống
> Right-click tray icon / Nhấn chuột phải vào icon

- **Enable** — Toggle on/off / Bật/tắt
- **Target Language** — Choose language / Chọn ngôn ngữ đích
- **Help / Hướng dẫn** — Built-in guide / Hướng dẫn sử dụng
- **Exit** — Quit app / Thoát

---

## 🛠️ Build from Source / Build từ mã nguồn

### Tauri v2 (Recommended)

**Prerequisites / Yêu cầu:** [Rust](https://rustup.rs/) + [Node.js](https://nodejs.org/)

```bash
git clone https://github.com/nguyennhuanhle/winTranslate.git
cd winTranslate/tauri-app
npm install
npm run tauri dev      # Dev mode
npm run tauri build    # Production build
```

Output: `src-tauri/target/release/bundle/nsis/winTranslate_*-setup.exe`

### Python v1 (Legacy)

```bash
cd winTranslate
uv venv && uv pip install -r requirements.txt
.venv\Scripts\python main.py
```

---

## 📁 Project Structure / Cấu trúc dự án

```
winTranslate/
├── tauri-app/                  # 🆕 Tauri v2 version (recommended)
│   ├── src/                    # Frontend (HTML/CSS/JS)
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── main.js
│   └── src-tauri/              # Rust backend
│       ├── src/lib.rs          # App logic, tray, hotkeys
│       ├── src/translate.rs    # Google Translate API
│       └── Cargo.toml
├── main.py                     # Python version entry point
├── translator.py               # Python translation module
├── selection_detector.py       # Python text selection
├── popup_ui.py                 # Python popup UI
├── tray_icon.py                # Python system tray
└── README.md
```

---

## ⚙️ How It Works / Cách hoạt động

```
[Select text] → [Ctrl+Shift+T] → [Auto Ctrl+C] → [Read clipboard] → [Google Translate API] → [Popup result]
```

1. **Global Hotkey** — Registers `Ctrl+Shift+T` system-wide / Đăng ký phím tắt toàn hệ thống
2. **Auto-Copy** — Simulates `Ctrl+C` via `enigo` / Giả lập `Ctrl+C` bằng `enigo`
3. **Translation** — Google Translate API (free, no key needed) / Google Translate (miễn phí)
4. **Popup** — WebView2 dark theme popup / Popup WebView2 giao diện tối

---

## 📋 Requirements / Yêu cầu

- Windows 10/11 or macOS 12+
- Internet connection / Kết nối mạng (Google Translate API)
- [WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (Windows — usually pre-installed)

## 👨‍💻 Author / Tác giả

**Mr Le Nguyen Nhu Anh** — [edtechcorner.com](https://edtechcorner.com/)

## 📄 License / Giấy phép

MIT License — see [LICENSE](LICENSE)
