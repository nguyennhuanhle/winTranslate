// winTranslate — Settings Panel Logic
const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;

// DOM elements
const targetLangSelect = document.getElementById('target-lang');
const autostartToggle = document.getElementById('autostart-toggle');
const showStartupToggle = document.getElementById('show-startup-toggle');
const saveStatus = document.getElementById('save-status');
const shortcutKey = document.getElementById('shortcut-key');

// OS-aware shortcut display
const isMac = navigator.platform.toUpperCase().includes('MAC')
    || navigator.userAgent.toUpperCase().includes('MAC');
shortcutKey.textContent = isMac ? '⌘+Shift+T' : 'Ctrl+Shift+T';

// Show a brief save status message
function showStatus(message, type) {
    saveStatus.textContent = message;
    saveStatus.className = 'footer-status ' + type;
    clearTimeout(showStatus._timer);
    showStatus._timer = setTimeout(() => {
        saveStatus.textContent = '';
        saveStatus.className = 'footer-status';
    }, 2000);
}

// Load current settings from Rust backend
async function loadSettings() {
    try {
        const settings = await invoke('get_settings');
        targetLangSelect.value = settings.target_lang || 'vi';
        autostartToggle.checked = settings.autostart || false;
        showStartupToggle.checked = settings.show_on_startup !== false; // default true
    } catch (e) {
        console.error('Failed to load settings:', e);
        showStatus('Failed to load settings', 'error');
    }
}

// Save a setting when it changes
async function saveSetting(key, value) {
    try {
        await invoke('save_setting', { key, value: JSON.stringify(value) });
        showStatus('✓ Saved', 'success');
    } catch (e) {
        console.error('Failed to save setting:', e);
        showStatus('Failed to save', 'error');
    }
}

// Event listeners — save immediately on change
targetLangSelect.addEventListener('change', () => {
    saveSetting('target_lang', targetLangSelect.value);
});

autostartToggle.addEventListener('change', () => {
    saveSetting('autostart', autostartToggle.checked);
});

showStartupToggle.addEventListener('change', () => {
    saveSetting('show_on_startup', showStartupToggle.checked);
});

// Listen for settings-reload event (when settings window is re-shown)
listen('reload-settings', () => {
    loadSettings();
});

// Initialize
loadSettings();
