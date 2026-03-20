use serde::Serialize;
use tauri::{
    menu::{CheckMenuItem, Menu, MenuItem, Submenu},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Emitter, Manager,
};

mod translate;

#[derive(Clone, Serialize)]
struct TranslatePayload {
    text: String,
    translated: String,
    error: Option<String>,
}

// Store the current target language
use std::sync::Mutex;

struct AppState {
    target_lang: Mutex<String>,
    enabled: Mutex<bool>,
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
        .manage(AppState {
            target_lang: Mutex::new("vi".to_string()),
            enabled: Mutex::new(true),
        })
        .invoke_handler(tauri::generate_handler![translate_text, resize_popup, hide_popup])
        .setup(|app| {
            // Build tray icon
            let tray_menu = create_tray_menu(app.handle(), true, "vi");

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

                        let enabled = *state.enabled.lock().unwrap();
                        let new_menu = create_tray_menu(app, enabled, &lang_code);
                        if let Some(tray) = app.tray_by_id("main-tray") {
                            let _ = tray.set_menu(Some(new_menu));
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
                                    // which MUST run on the main thread. Since we're in a spawned thread,
                                    // use osascript to simulate Cmd+C instead — works from any thread.
                                    std::thread::sleep(std::time::Duration::from_millis(200));

                                    let _ = std::process::Command::new("osascript")
                                        .arg("-e")
                                        .arg("tell application \"System Events\" to keystroke \"c\" using command down")
                                        .output();

                                    // Wait for clipboard to update
                                    std::thread::sleep(std::time::Duration::from_millis(200));
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

