// winTranslate - Frontend Logic
const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;
const { readText, writeText } = window.__TAURI__.clipboardManager;

// OS-aware shortcut display
const isMac = navigator.platform.toUpperCase().includes('MAC')
    || navigator.userAgent.toUpperCase().includes('MAC');
const SHORTCUT_KEY = isMac ? '⌘+Shift+T' : 'Ctrl+Shift+T';

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
const updateSection = document.getElementById("update-section");
const updateInfo = document.getElementById("update-info");
const updateBtn = document.getElementById("update-btn");
const updateProgress = document.getElementById("update-progress");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");

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
    updateSection.classList.add("hidden");
    updateProgress.classList.add("hidden");
    statusText.innerHTML = `Press <kbd>${SHORTCUT_KEY}</kbd> to translate`;
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
            showError(`No text found. Select text first, then press ${SHORTCUT_KEY}.`);
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

// Listen for check-update trigger from Rust backend
let pendingUpdate = null;
listen("check-update", async () => {
    resetUI();
    statusText.innerHTML = '🔍 Checking for updates...';
    loading.classList.remove("hidden");
    await resizeToFit();

    try {
        const { check } = await import("@tauri-apps/plugin-updater");
        const update = await check();

        loading.classList.add("hidden");

        if (update) {
            pendingUpdate = update;
            statusText.innerHTML = '🆕 Update available!';
            updateInfo.innerHTML = `<strong>Version ${update.version}</strong> is available.${update.body ? '<br><br>' + update.body : ''}`;
            updateSection.classList.remove("hidden");
            updateBtn.disabled = false;
            updateBtn.textContent = '⬇️ Install & Restart';
            updateProgress.classList.add("hidden");
        } else {
            statusText.innerHTML = '✅ You are on the latest version!';
        }
        await resizeToFit();
    } catch (e) {
        loading.classList.add("hidden");
        showError("Update check failed: " + e.toString());
    }
});

// Handle update install button
document.getElementById("update-btn").addEventListener("click", async () => {
    if (!pendingUpdate) return;

    updateBtn.disabled = true;
    updateBtn.textContent = 'Downloading...';
    updateProgress.classList.remove("hidden");
    progressFill.style.width = '0%';
    await resizeToFit();

    try {
        let downloaded = 0;
        let contentLength = 0;

        await pendingUpdate.downloadAndInstall((event) => {
            switch (event.event) {
                case 'Started':
                    contentLength = event.data.contentLength || 0;
                    progressText.textContent = 'Starting download...';
                    break;
                case 'Progress':
                    downloaded += event.data.chunkLength;
                    if (contentLength > 0) {
                        const pct = Math.min(100, Math.round((downloaded / contentLength) * 100));
                        progressFill.style.width = pct + '%';
                        progressText.textContent = `${pct}% (${(downloaded / 1024 / 1024).toFixed(1)} MB)`;
                    } else {
                        progressText.textContent = `${(downloaded / 1024 / 1024).toFixed(1)} MB downloaded`;
                    }
                    break;
                case 'Finished':
                    progressFill.style.width = '100%';
                    progressText.textContent = 'Download complete! Restarting...';
                    updateBtn.textContent = '🔄 Restarting...';
                    break;
            }
        });

        // Relaunch after install
        const { relaunch } = await import("@tauri-apps/plugin-process");
        await relaunch();
    } catch (e) {
        updateBtn.disabled = false;
        updateBtn.textContent = '⬇️ Install & Restart';
        updateProgress.classList.add("hidden");
        showError("Update failed: " + e.toString());
    }
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

// Initialize — update all shortcut labels for current OS
document.querySelectorAll('.shortcut-key').forEach(el => {
    el.textContent = SHORTCUT_KEY;
});
resetUI();
resizeToFit();
