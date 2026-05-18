use serde::Serialize;
use tauri::{AppHandle, Emitter, Manager, Runtime};

const MAIN_WINDOW_LABEL: &str = "main";
const DEFAULT_WEB_URL: &str = "http://localhost:3000";

#[derive(Clone, Debug, Serialize)]
pub struct NavigatePayload {
    pub url: String,
    pub argv: Vec<String>,
    pub cwd: String,
}

pub fn attach<R: Runtime>(builder: tauri::Builder<R>) -> tauri::Builder<R> {
    builder.plugin(tauri_plugin_single_instance::init(|app, argv, cwd| {
        focus_and_emit(app, configured_web_url(), argv, cwd);
    }))
}

#[tauri::command]
pub fn focus_main_window(app: AppHandle) -> Result<(), String> {
    focus_window(&app).map_err(|error| error.to_string())
}

#[tauri::command]
pub fn navigate_existing_window(app: AppHandle, url: String) -> Result<(), String> {
    focus_and_emit(&app, url, Vec::new(), String::new());
    Ok(())
}

pub fn navigate_to_configured_web_url(app: &AppHandle) {
    let url = configured_web_url();
    if url != DEFAULT_WEB_URL {
        focus_and_emit(app, url, Vec::new(), String::new());
    }
}

fn configured_web_url() -> String {
    std::env::var("MANTLE_WEB_URL").unwrap_or_else(|_| DEFAULT_WEB_URL.to_string())
}

fn focus_and_emit(app: &AppHandle, url: String, argv: Vec<String>, cwd: String) {
    let _ = focus_window(app);
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        let _ = window.emit("tauri://navigate", NavigatePayload { url, argv, cwd });
    }
}

fn focus_window(app: &AppHandle) -> tauri::Result<()> {
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        window.unminimize()?;
        window.set_focus()?;
    }
    Ok(())
}
