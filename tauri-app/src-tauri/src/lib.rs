use serde::{Deserialize, Serialize};
use tauri::{
    menu::{CheckMenuItem, Menu, MenuItem, Submenu},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Emitter, Manager,
};
use tauri_plugin_autostart::MacosLauncher;
use tauri_plugin_autostart::ManagerExt;
use tauri_plugin_store::StoreExt;

mod translate;

#[derive(Clone, Serialize)]
struct TranslatePayload {
    text: String,
    translated: String,
    error: Option<String>,
}

// Store the current target language and enabled state
use std::sync::Mutex;

struct AppState {
    target_lang: Mutex<String>,
    enabled: Mutex<bool>,
}

#[derive(Serialize, Deserialize)]
struct SettingsResponse {
    target_lang: String,
    autostart: bool,
    show_on_startup: bool,
}

#[tauri::command]
async fn translate_text(
    text: String,
    state: tauri::State<'_, AppState>,
) -> Result<TranslatePayload, String> {
    let target = state.target_lang.lock().unwrap().clone();

    match translate::google_translate(&text, &target).await {
        Ok(translated) => Ok(TranslatePayload {
            text: text.clone(),
            translated,
            error: None,
        }),
        Err(e) => Ok(TranslatePayload {
            text: text.clone(),
            translated: String::new(),
            error: Some(e.to_string()),
        }),
    }
}

#[tauri::command]
async fn resize_popup(app: AppHandle, width: f64, height: f64) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        let size = tauri::LogicalSize::new(width, height);
        window
            .set_size(tauri::Size::Logical(size))
            .map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
async fn hide_popup(app: AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        window.hide().map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
async fn get_settings(app: AppHandle) -> Result<SettingsResponse, String> {
    let store = app.store("settings.json").map_err(|e| e.to_string())?;

    let target_lang = store
        .get("target_lang")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| "vi".to_string());

    let autostart = store
        .get("autostart")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);

    let show_on_startup = store
        .get("show_on_startup")
        .and_then(|v| v.as_bool())
        .unwrap_or(true);

    Ok(SettingsResponse {
        target_lang,
        autostart,
        show_on_startup,
    })
}

#[tauri::command]
async fn save_setting(app: AppHandle, key: String, value: String) -> Result<(), String> {
    let store = app.store("settings.json").map_err(|e| e.to_string())?;

    // Parse the JSON value
    let parsed: serde_json::Value =
        serde_json::from_str(&value).map_err(|e| e.to_string())?;

    store.set(key.clone(), parsed.clone());

    // If target_lang changed, update app state and tray
    if key == "target_lang" {
        if let Some(lang) = parsed.as_str() {
            let state = app.state::<AppState>();
            *state.target_lang.lock().unwrap() = lang.to_string();

            let enabled = *state.enabled.lock().unwrap();
            let new_menu = create_tray_menu(&app, enabled, lang);
            if let Some(tray) = app.tray_by_id("main-tray") {
                let _ = tray.set_menu(Some(new_menu));
            }
        }
    }

    // If autostart changed, toggle it
    if key == "autostart" {
        if let Some(enabled) = parsed.as_bool() {
            let autostart_manager = app.autolaunch();
            if enabled {
                let _ = autostart_manager.enable();
            } else {
                let _ = autostart_manager.disable();
            }
        }
    }

    Ok(())
}

fn create_tray_menu(app: &AppHandle, enabled: bool, current_lang: &str) -> Menu<tauri::Wry> {
    let langs: Vec<(&str, &str)> = vec![
        ("vi", "Tiếng Việt"),
        ("en", "English"),
        ("zh-CN", "中文 (简体)"),
        ("zh-TW", "中文 (繁體)"),
        ("ja", "日本語"),
        ("ko", "한국어"),
        ("fr", "Français"),
        ("de", "Deutsch"),
        ("es", "Español"),
        ("th", "ภาษาไทย"),
        ("ru", "Русский"),
    ];

    let enable_item =
        CheckMenuItem::with_id(app, "toggle", "Enable", true, enabled, None::<&str>)
            .expect("failed to create menu item");

    let lang_submenu = Submenu::with_id(app, "languages", "Target Language", true)
        .expect("failed to create submenu");

    for (code, name) in &langs {
        let item = CheckMenuItem::with_id(
            app,
            format!("lang_{}", code),
            *name,
            true,
            *code == current_lang,
            None::<&str>,
        )
        .expect("failed to create lang item");
        lang_submenu.append(&item).expect("failed to append");
    }

    let settings_item =
        MenuItem::with_id(app, "settings", "Settings / Cài đặt", true, None::<&str>)
            .expect("failed to create settings item");

    let help_item =
        MenuItem::with_id(app, "help", "Help / Hướng dẫn", true, None::<&str>)
            .expect("failed to create help item");

    let update_item =
        MenuItem::with_id(app, "check_update", "Check for Updates", true, None::<&str>)
            .expect("failed to create update item");

    let quit_item =
        MenuItem::with_id(app, "quit", "Exit", true, None::<&str>).expect("failed to create quit");

    let menu = Menu::new(app).expect("failed to create menu");
    menu.append(&enable_item).unwrap();
    menu.append(&lang_submenu).unwrap();
    menu.append(&settings_item).unwrap();
    menu.append(&help_item).unwrap();
    menu.append(&update_item).unwrap();
    menu.append(&quit_item).unwrap();
    menu
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_autostart::init(
            MacosLauncher::LaunchAgent,
            None,
        ))
        .manage(AppState {
            target_lang: Mutex::new("vi".to_string()),
            enabled: Mutex::new(true),
        })
        .invoke_handler(tauri::generate_handler![
            translate_text,
            resize_popup,
            hide_popup,
            get_settings,
            save_setting,
        ])
        .setup(|app| {
            // Load saved settings from store
            {
                let store = app.handle().store("settings.json").ok();
                if let Some(ref store) = store {
                    // Restore target language
                    if let Some(lang) = store.get("target_lang").and_then(|v| v.as_str().map(String::from)) {
                        let state = app.state::<AppState>();
                        *state.target_lang.lock().unwrap() = lang;
                    }
                }
            }

            let state = app.state::<AppState>();
            let current_lang = state.target_lang.lock().unwrap().clone();

            // Build tray icon
            let tray_menu = create_tray_menu(app.handle(), true, &current_lang);

            let _tray = TrayIconBuilder::with_id("main-tray")
                .menu(&tray_menu)
                .tooltip(if cfg!(target_os = "macos") {
                    "winTranslate — ⌘+Shift+T to translate"
                } else {
                    "winTranslate — Ctrl+Shift+T to translate"
                })
                .on_menu_event(move |app, event| {
                    let id = event.id().as_ref();

                    if id == "toggle" {
                        let state = app.state::<AppState>();
                        let mut enabled = state.enabled.lock().unwrap();
                        *enabled = !*enabled;
                        let is_enabled = *enabled;
                        drop(enabled);

                        let lang = state.target_lang.lock().unwrap().clone();
                        let new_menu = create_tray_menu(app, is_enabled, &lang);
                        if let Some(tray) = app.tray_by_id("main-tray") {
                            let _ = tray.set_menu(Some(new_menu));
                        }
                    } else if id.starts_with("lang_") {
                        let lang_code = id.strip_prefix("lang_").unwrap().to_string();
                        let state = app.state::<AppState>();
                        *state.target_lang.lock().unwrap() = lang_code.clone();

                        // Also save to store
                        if let Ok(store) = app.store("settings.json") {
                            store.set("target_lang", serde_json::json!(lang_code));
                        }

                        let enabled = *state.enabled.lock().unwrap();
                        let new_menu = create_tray_menu(app, enabled, &lang_code);
                        if let Some(tray) = app.tray_by_id("main-tray") {
                            let _ = tray.set_menu(Some(new_menu));
                        }
                    } else if id == "settings" {
                        // Show settings window
                        if let Some(window) = app.get_webview_window("settings") {
                            let _ = window.show();
                            let _ = window.set_focus();
                            let _ = app.emit_to("settings", "reload-settings", ());
                        }
                    } else if id == "help" {
                        // Show help window
                        let _ = app.emit("show-help", ());
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    } else if id == "check_update" {
                        let _ = app.emit("check-update", ());
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    } else if id == "quit" {
                        app.exit(0);
                    }
                })
                .on_tray_icon_event(|_tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        // Left-click on tray
                    }
                })
                .icon(
                    tauri::image::Image::from_bytes(include_bytes!("../icons/icon.png"))
                        .expect("failed to load tray icon"),
                )
                .icon_as_template(false)
                .build(app)?;

            // Intercept close on settings window — hide instead of quit
            if let Some(settings_window) = app.get_webview_window("settings") {
                settings_window.on_window_event(move |event| {
                    if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                        api.prevent_close();
                        // The window handle from the event doesn't give us direct access,
                        // but we already captured settings_window in the outer scope.
                        // We need to hide via a different approach — emit an event.
                    }
                });
            }

            // Use a window-level close handler via the app handle
            let app_handle_for_close = app.handle().clone();
            if let Some(settings_window) = app.get_webview_window("settings") {
                settings_window.on_window_event(move |event| {
                    if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                        api.prevent_close();
                        if let Some(win) = app_handle_for_close.get_webview_window("settings") {
                            let _ = win.hide();
                        }
                    }
                });
            }

            // Show settings window on startup if preference allows
            {
                let should_show = app
                    .handle()
                    .store("settings.json")
                    .ok()
                    .and_then(|store| store.get("show_on_startup").and_then(|v| v.as_bool()))
                    .unwrap_or(true); // default: show on startup

                if should_show {
                    if let Some(settings_window) = app.get_webview_window("settings") {
                        let _ = settings_window.show();
                        let _ = settings_window.set_focus();
                    }
                }
            }

            // Register global shortcut: Ctrl+Shift+T (or Cmd+Shift+T on macOS)
            use tauri_plugin_global_shortcut::{GlobalShortcutExt, ShortcutState};

            #[cfg(target_os = "macos")]
            let shortcut_str = "Cmd+Shift+T";
            #[cfg(not(target_os = "macos"))]
            let shortcut_str = "Ctrl+Shift+T";

            let app_handle = app.handle().clone();

            app.handle().plugin(
                tauri_plugin_global_shortcut::Builder::new()
                    .with_handler(move |_app, _shortcut, event| {
                        if event.state() == ShortcutState::Pressed {
                            let state = app_handle.state::<AppState>();
                            let enabled = *state.enabled.lock().unwrap();
                            if !enabled {
                                return;
                            }

                            let handle = app_handle.clone();

                            // Spawn async task to:
                            // 1. Simulate Ctrl+C to copy selected text
                            // 2. Read clipboard
                            // 3. Emit text to frontend
                            std::thread::spawn(move || {
                                // Platform-specific copy simulation
                                #[cfg(target_os = "macos")]
                                {
                                    // On macOS, enigo's Key::Unicode calls TSMGetInputSourceProperty
                                    // which MUST run on the main thread. Use CGEvent API directly
                                    // instead — it's thread-safe and much faster than osascript.
                                    use std::ptr;

                                    extern "C" {
                                        fn CGEventCreateKeyboardEvent(
                                            source: *const std::ffi::c_void,
                                            keycode: u16,
                                            key_down: bool,
                                        ) -> *mut std::ffi::c_void;
                                        fn CGEventSetFlags(event: *mut std::ffi::c_void, flags: u64);
                                        fn CGEventPost(tap: u32, event: *mut std::ffi::c_void);
                                        fn CFRelease(cf: *mut std::ffi::c_void);
                                    }

                                    // macOS virtual keycodes
                                    const KC_C: u16 = 8;
                                    const KC_T: u16 = 17;
                                    // CGEvent flag for Cmd key
                                    const K_CG_EVENT_FLAG_COMMAND: u64 = 0x00100000;
                                    // kCGHIDEventTap = 0
                                    const K_CG_HID_EVENT_TAP: u32 = 0;

                                    // Wait for user to release hotkey keys (Cmd+Shift+T)
                                    std::thread::sleep(std::time::Duration::from_millis(150));

                                    unsafe {
                                        // Release 'T' key (in case still held from hotkey)
                                        let ev = CGEventCreateKeyboardEvent(ptr::null(), KC_T, false);
                                        if !ev.is_null() {
                                            CGEventPost(K_CG_HID_EVENT_TAP, ev);
                                            CFRelease(ev);
                                        }

                                        std::thread::sleep(std::time::Duration::from_millis(50));

                                        // Press Cmd+C (key down)
                                        let ev = CGEventCreateKeyboardEvent(ptr::null(), KC_C, true);
                                        if !ev.is_null() {
                                            CGEventSetFlags(ev, K_CG_EVENT_FLAG_COMMAND);
                                            CGEventPost(K_CG_HID_EVENT_TAP, ev);
                                            CFRelease(ev);
                                        }

                                        std::thread::sleep(std::time::Duration::from_millis(20));

                                        // Release Cmd+C (key up)
                                        let ev = CGEventCreateKeyboardEvent(ptr::null(), KC_C, false);
                                        if !ev.is_null() {
                                            CGEventSetFlags(ev, K_CG_EVENT_FLAG_COMMAND);
                                            CGEventPost(K_CG_HID_EVENT_TAP, ev);
                                            CFRelease(ev);
                                        }
                                    }

                                    // Wait for clipboard to update
                                    std::thread::sleep(std::time::Duration::from_millis(300));
                                }

                                #[cfg(not(target_os = "macos"))]
                                {
                                    // On Windows/Linux, use enigo to simulate Ctrl+C
                                    if let Ok(mut enigo) = enigo::Enigo::new(&enigo::Settings::default()) {
                                        use enigo::{Keyboard, Key, Direction};

                                        // Release all modifier keys from the hotkey first
                                        // When user presses Ctrl+Shift+T, those keys are still held
                                        let _ = enigo.key(Key::Shift, Direction::Release);
                                        let _ = enigo.key(Key::Control, Direction::Release);
                                        let _ = enigo.key(Key::Unicode('t'), Direction::Release);

                                        // Wait for keys to fully release
                                        std::thread::sleep(std::time::Duration::from_millis(100));

                                        // Now simulate a clean Ctrl+C
                                        let _ = enigo.key(Key::Control, Direction::Press);
                                        std::thread::sleep(std::time::Duration::from_millis(20));
                                        let _ = enigo.key(Key::Unicode('c'), Direction::Click);
                                        std::thread::sleep(std::time::Duration::from_millis(20));
                                        let _ = enigo.key(Key::Control, Direction::Release);

                                        // Wait for clipboard to update
                                        std::thread::sleep(std::time::Duration::from_millis(200));
                                    }
                                }

                                // Emit event to frontend with clipboard text
                                let _ = handle.emit("trigger-translate", ());

                                // Show and focus the window
                                if let Some(window) = handle.get_webview_window("main") {
                                    let _ = window.show();
                                    let _ = window.set_focus();
                                }
                            });
                        }
                    })
                    .build(),
            )?;

            // Register the shortcut
            app.global_shortcut().register(shortcut_str)?;

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
