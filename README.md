# winTranslate

> 🇬🇧 Cross-platform text translation — select text anywhere, get instant translation.
> 
> 🇻🇳 Dịch văn bản đa nền tảng — bôi đen chữ ở bất kỳ đâu, dịch ngay lập tức.

![Tauri](https://img.shields.io/badge/Tauri-v2-blue?logo=tauri)
![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange?logo=rust)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-0078D6)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📥 Download / Tải về

| Version | Platform | Download |
|---------|----------|----------|
| **Tauri v2** ⭐ | Windows x64 | [📥 Latest Release](../../releases/latest) |
| **Tauri v2** ⭐ | macOS (Apple Silicon) | [📥 v2.1.0](../../releases/tag/v2.1.0) |
| v1.0 (Python) | Windows | [winTranslate.exe](../../releases/tag/v1.0) |

> **Recommended / Khuyên dùng:** Tauri v2 — nhẹ hơn (4 MB vs 22 MB), nhanh hơn, UI đẹp hơn.

---

## ✨ Features / Tính năng

- ⌨️ **Hotkey / Phím tắt** — `Ctrl+Shift+T` (Win) / `⌘+Shift+T` (Mac) — auto-copy & translate / tự copy và dịch
- 🌐 **Auto-detect / Tự nhận diện** — Source language auto-detected / Tự nhận diện ngôn ngữ nguồn
- 🎯 **11 Languages / 11 Ngôn ngữ** — Vietnamese, English, 中文, 日本語, 한국어, Français, Deutsch, Español, ภาษาไทย, Русский, 中文繁體
- 🔄 **Toggle / Bật/Tắt** — System tray enable/disable / Bật tắt qua khay hệ thống
- 📋 **Copy** — One-click copy translation / Bấm 1 lần để copy bản dịch
- 🎨 **Dark Theme** — Catppuccin Mocha color scheme / Giao diện tối hiện đại
- 📖 **Built-in Help / Hướng dẫn tích hợp** — Bilingual guide / Song ngữ Anh-Việt
- 🖥️ **Cross-platform / Đa nền tảng** — Windows & macOS

---

## 🚀 Usage / Cách sử dụng

1. **Run / Chạy** — Launch app → icon appears in system tray (Win) or menu bar (Mac) / Chạy app → icon xuất hiện ở khay hệ thống (Win) hoặc thanh menu (Mac)
2. **Select text / Bôi đen chữ** — In any app / Ở bất kỳ ứng dụng nào
3. **Press / Nhấn** `Ctrl+Shift+T` (Win) hoặc `⌘+Shift+T` (Mac) — Popup appears with translation / Popup hiện ra với bản dịch
4. **Copy / Sao chép** — Click Copy button / Bấm nút Copy
5. **Close / Đóng** — Click ✕ or press `Esc` / Bấm ✕ hoặc nhấn `Esc`

### System Tray / Khay hệ thống
> Right-click tray icon (Win) or click menu bar icon (Mac) / Nhấn chuột phải vào icon (Win) hoặc nhấn icon trên menu bar (Mac)

- **Enable** — Toggle on/off / Bật/tắt
- **Target Language** — Choose language / Chọn ngôn ngữ đích
- **Help / Hướng dẫn** — Built-in guide / Hướng dẫn sử dụng
- **Check for Updates** — Check for new version / Kiểm tra bản cập nhật
- **Exit** — Quit app / Thoát

---

## 🍎 macOS — Installation & Permissions / Cài đặt & Cấp quyền

### Step 1 / Bước 1: Install / Cài đặt

1. Download file `.zip` from [Releases v2.1.0](../../releases/tag/v2.1.0) / Tải file `.zip` từ [Releases v2.1.0](../../releases/tag/v2.1.0)
2. Unzip → drag `winTranslate.app` into `/Applications` / Giải nén → kéo `winTranslate.app` vào `/Applications`

### Step 2 / Bước 2: First launch / Mở lần đầu

macOS will block the app because it is not signed. / macOS sẽ chặn app vì chưa được ký.

1. Right-click `winTranslate.app` → **Open** → click **Open** again / Nhấn chuột phải vào app → **Open** → nhấn **Open** lần nữa
2. Or go to **System Settings → Privacy & Security** → scroll down → click **Open Anyway** / Hoặc vào **Cài đặt Hệ thống → Quyền riêng tư & Bảo mật** → cuộn xuống → nhấn **Mở bất kỳ**

### Step 3 / Bước 3: Grant Accessibility permission / Cấp quyền Accessibility

> ⚠️ **Required / Bắt buộc:** Without this permission, the app cannot detect your selected text. / Không có quyền này, app không thể nhận diện văn bản bạn bôi đen.

1. Open **System Settings** → **Privacy & Security** → **Accessibility** / Mở **Cài đặt hệ thống** → **Quyền riêng tư & Bảo mật** → **Trợ năng (Accessibility)**
2. Click the **+** button → navigate to `/Applications` → select **winTranslate** → click **Open** / Nhấn nút **+** → tìm đến `/Applications` → chọn **winTranslate** → nhấn **Open**
3. Make sure the toggle is **ON** (blue) / Đảm bảo toggle đã **BẬT** (xanh)
4. **Quit and relaunch** the app / **Tắt và mở lại** app

> 💡 If the app was updated, you may need to remove it from the Accessibility list and re-add it. / Nếu app được cập nhật, bạn có thể cần xoá khỏi danh sách Accessibility rồi thêm lại.

---

## 🛠️ Build from Source / Build từ mã nguồn

### Prerequisites / Yêu cầu

| | Windows | macOS |
|---|---------|-------|
| **Rust** | [rustup.rs](https://rustup.rs/) | [rustup.rs](https://rustup.rs/) |
| **Node.js** | [nodejs.org](https://nodejs.org/) | [nodejs.org](https://nodejs.org/) or `brew install node` |
| **Build tools** | — | `xcode-select --install` |

### Build commands / Lệnh build

```bash
git clone https://github.com/nguyennhuanhle/winTranslate.git
cd winTranslate/tauri-app
npm install
npm run tauri dev      # Dev mode
npm run tauri build    # Production build
```

### Output

| Platform | File |
|----------|------|
| Windows | `src-tauri/target/release/bundle/nsis/winTranslate_*-setup.exe` |
| macOS | `src-tauri/target/release/bundle/macos/winTranslate.app` |

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
[Select text] → [Hotkey] → [Auto Copy] → [Read clipboard] → [Google Translate API] → [Popup result]
```

1. **Global Hotkey** — Registers `Ctrl+Shift+T` (Win) / `⌘+Shift+T` (Mac) system-wide / Đăng ký phím tắt toàn hệ thống
2. **Auto-Copy** — Simulates `Ctrl+C` (Win via `enigo`) or `⌘+C` (Mac via `CGEvent` API) / Giả lập copy tự động
3. **Translation** — Google Translate API (free, no key needed) / Google Translate (miễn phí)
4. **Popup** — WebView dark theme popup / Popup WebView giao diện tối

---

## 📋 Requirements / Yêu cầu

### Windows
- Windows 10/11
- Internet connection / Kết nối mạng
- [WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (usually pre-installed / thường đã có sẵn)

### macOS
- macOS 12 (Monterey) or later / macOS 12 trở lên
- Apple Silicon (M1/M2/M3/M4) or Intel
- Internet connection / Kết nối mạng
- Accessibility permission (see [macOS Installation guide](#-macos--installation--permissions--cài-đặt--cấp-quyền) above) / Quyền Accessibility (xem [hướng dẫn cài đặt macOS](#-macos--installation--permissions--cài-đặt--cấp-quyền) ở trên)

---

## 👨‍💻 Author / Tác giả

**Mr Le Nguyen Nhu Anh** — [edtechcorner.com](https://edtechcorner.com/)

## 📄 License / Giấy phép

MIT License — see [LICENSE](LICENSE)
