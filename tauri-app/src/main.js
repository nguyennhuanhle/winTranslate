// winTranslate - Frontend Logic
const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;
const { readText, writeText } = window.__TAURI__.clipboardManager;

let appWindow = null;
try {
    const { getCurrentWindow } = window.__TAURI__.window;
    appWindow = getCurrentWindow();
} catch(e) {
    console.error("Window API not available:", e);
}

// DOM elements
const appEl = document.getElementById("app");
const statusText = document.getElementById("status-text");
const originalSection = document.getElementById("original-section");
const originalText = document.getElementById("original-text");
const loading = document.getElementById("loading");
const resultSection = document.getElementById("result-section");
const translatedText = document.getElementById("translated-text");
const copyBtn = document.getElementById("copy-btn");
const copyIcon = document.getElementById("copy-icon");
const copyLabel = document.getElementById("copy-label");
const errorSection = document.getElementById("error-section");
const errorText = document.getElementById("error-text");
const closeBtn = document.getElementById("close-btn");
const helpSection = document.getElementById("help-section");

const POPUP_WIDTH = 420;
const MAX_HEIGHT = 600;
const MIN_HEIGHT = 60;

// Resize window via Rust command (reliable, no JS API issues)
async function resizeToFit() {
    await new Promise(r => setTimeout(r, 50));
    // Measure each section individually to get true content height
    const statusH = document.getElementById("status-bar").scrollHeight || 0;
    const contentH = document.getElementById("scroll-content").scrollHeight || 0;
    const footerH = document.getElementById("footer").scrollHeight || 0;
    const totalH = statusH + contentH + footerH + 40; // +padding
    const height = Math.max(MIN_HEIGHT, Math.min(totalH, MAX_HEIGHT));
    try {
        await invoke("resize_popup", { width: POPUP_WIDTH, height: height });
    } catch (e) {
        console.error("Resize failed:", e);
    }
}

// Hide popup via Rust command
async function hidePopup() {
    try {
        await invoke("hide_popup");
    } catch (e) {
        console.error("Hide failed:", e);
    }
    resetUI();
}

// Reset UI to initial state
function resetUI() {
    originalSection.classList.add("hidden");
    loading.classList.add("hidden");
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");
    helpSection.classList.add("hidden");
    statusText.innerHTML = 'Press <kbd>Ctrl+Shift+T</kbd> to translate';
}

// Show original text
function showOriginal(text) {
    const truncated = text.length > 500 ? text.substring(0, 500) + "..." : text;
    originalText.textContent = truncated;
    originalSection.classList.remove("hidden");
    resizeToFit();
}

// Show loading
function showLoading() {
    loading.classList.remove("hidden");
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");
    resizeToFit();
}

// Show result
function showResult(translated) {
    loading.classList.add("hidden");
    translatedText.textContent = translated;
    resultSection.classList.remove("hidden");
    statusText.innerHTML = '✅ Done!';
    resizeToFit();
}

// Show error
function showError(message) {
    loading.classList.add("hidden");
    errorText.textContent = message;
    errorSection.classList.remove("hidden");
    resizeToFit();
}

// Close button - invoke Rust directly
closeBtn.addEventListener("click", function(e) {
    e.preventDefault();
    e.stopPropagation();
    hidePopup();
});

// Copy translation
copyBtn.addEventListener("click", async function(e) {
    e.preventDefault();
    e.stopPropagation();
    const text = translatedText.textContent;
    if (!text) return;

    try {
        await writeText(text);
        copyIcon.textContent = "✅";
        copyLabel.textContent = "Copied!";
        copyBtn.classList.add("copied");

        setTimeout(() => {
            copyIcon.textContent = "📋";
            copyLabel.textContent = "Copy";
            copyBtn.classList.remove("copied");
        }, 1500);
    } catch (err) {
        console.error("Copy failed:", err);
    }
});

// Listen for translate trigger from Rust backend
listen("trigger-translate", async () => {
    resetUI();
    await resizeToFit();

    try {
        const clipText = await readText();

        if (!clipText || !clipText.trim()) {
            showError("No text found. Select text first, then press Ctrl+Shift+T.");
            return;
        }

        const text = clipText.trim();
        showOriginal(text);
        showLoading();

        const result = await invoke("translate_text", { text });

        if (result.error) {
            showError(result.error);
        } else {
            showResult(result.translated);
        }
    } catch (e) {
        showError("Translation failed: " + e.toString());
    }
});

// Listen for help trigger from Rust backend
listen("show-help", () => {
    resetUI();
    statusText.innerHTML = '📖 Help / Hướng dẫn';
    helpSection.classList.remove("hidden");
    resizeToFit();
});

// Escape to close
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        hidePopup();
    }
});

// Drag window by status bar
document.getElementById("status-bar").addEventListener("mousedown", (e) => {
    if (e.target.id !== "close-btn" && appWindow) {
        try {
            appWindow.startDragging();
        } catch(err) {
            console.error("Drag failed:", err);
        }
    }
});

// Initialize
resetUI();
resizeToFit();
