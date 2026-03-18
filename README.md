# winTranslate

> 🇬🇧 System-wide text translation for Windows — select text anywhere, get instant translation.
> 
> 🇻🇳 Dịch văn bản toàn hệ thống trên Windows — bôi đen chữ ở bất kỳ đâu, dịch ngay lập tức.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features / Tính năng

- 🌐 **Instant Translation / Dịch nhanh** — Select text in any app → popup appears → click Translate / Bôi đen chữ → popup hiện ra → bấm Translate
- 🔍 **Auto-detect Language / Tự nhận diện ngôn ngữ** — English, Chinese, Japanese, Korean, French, German, and more / Tiếng Anh, Trung, Nhật, Hàn, Pháp, Đức, v.v.
- 🎯 **Multiple Target Languages / Nhiều ngôn ngữ đích** — Vietnamese, English, 中文, 日本語, 한국어, Français, Deutsch, Español, ภาษาไทย, Русский
- 🔄 **Toggle On/Off / Bật/Tắt** — Enable or disable via system tray / Bật tắt qua system tray, không ảnh hưởng Windows
- 📋 **Copy Result / Sao chép kết quả** — One-click copy translation / Bấm 1 lần để copy bản dịch
- 🎨 **Dark Theme UI / Giao diện tối** — Clean popup with Catppuccin Mocha colors / Popup đẹp, hiện đại

---

## 📦 Installation / Cài đặt

### Option 1: Download Executable (Recommended) / Tải file chạy (Khuyên dùng)

Download `winTranslate.exe` from [Releases](../../releases) — no Python needed.

Tải `winTranslate.exe` từ [Releases](../../releases) — không cần cài Python.

### Option 2: Run from Source / Chạy từ mã nguồn

```bash
git clone https://github.com/nguyennhuanhle/winTranslate.git
cd winTranslate
uv venv
uv pip install -r requirements.txt
.venv\Scripts\python main.py
```

---

## 🚀 Usage / Cách sử dụng

1. **Run / Chạy** `winTranslate.exe` or `python main.py`
2. **Look for / Tìm** the blue "T" icon in the system tray / icon chữ "T" màu xanh ở khay hệ thống
3. **Select text / Bôi đen chữ** in any application / ở bất kỳ ứng dụng nào
4. **Click "🌐 Translate"** in the popup / trong popup hiện ra gần chuột
5. **View & Copy / Xem & Copy** the translation result / kết quả dịch

### System Tray Options / Tuỳ chọn khay hệ thống
> Right-click the "T" icon / Nhấn chuột phải vào icon "T"

- **Enable / Disable** — Toggle monitoring / Bật/tắt theo dõi
- **Target Language** — Choose translation language / Chọn ngôn ngữ đích
- **Exit** — Quit the app / Thoát ứng dụng

---

## 🛠️ Build from Source / Tự build

```bash
# Install dependencies / Cài thư viện
uv pip install -r requirements.txt
uv pip install pyinstaller

# Generate icon / Tạo icon
.venv\Scripts\python create_icon.py

# Build exe
.venv\Scripts\pyinstaller --onefile --windowed --name winTranslate --icon app.ico --add-data "app.ico;." main.py
```

Output: `dist/winTranslate.exe`

---

## 📁 Project Structure / Cấu trúc dự án

```
winTranslate/
├── main.py              # Entry point / Điểm vào
├── translator.py        # Translation engine / Module dịch (Google Translate)
├── selection_detector.py # Text selection detection / Phát hiện bôi đen chữ
├── popup_ui.py          # Floating popup UI / Giao diện popup
├── tray_icon.py         # System tray icon / Icon khay hệ thống
├── create_icon.py       # Icon generator / Tạo icon cho exe
├── requirements.txt     # Dependencies / Thư viện cần thiết
└── run.bat              # Quick-launch / Chạy nhanh
```

---

## ⚙️ How It Works / Cách hoạt động

1. **Mouse Monitoring / Theo dõi chuột** — Uses `pynput` to detect drag-select gestures / Dùng `pynput` phát hiện thao tác kéo chọn
2. **Clipboard Capture / Đọc clipboard** — Simulates `Ctrl+C`, reads clipboard, restores original / Giả lập `Ctrl+C`, đọc clipboard, khôi phục clipboard gốc
3. **Translation / Dịch thuật** — Google Translate via `deep-translator` (auto-detect source) / Dùng Google Translate, tự nhận diện ngôn ngữ nguồn
4. **Popup Display / Hiển thị** — Tkinter floating window near cursor / Cửa sổ nhỏ hiện gần con trỏ chuột

---

## 📋 Requirements / Yêu cầu

- Windows 10/11
- Internet connection / Kết nối mạng (uses Google Translate API)
- Python 3.10+ (only if running from source / chỉ khi chạy từ mã nguồn)

## 📄 License / Giấy phép

MIT License
