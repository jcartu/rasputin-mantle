use tauri::menu::{MenuBuilder, MenuItemBuilder, PredefinedMenuItem, SubmenuBuilder};
use tauri::{App, Emitter, Manager};

pub fn install(app: &mut App) -> tauri::Result<()> {
    let handle = app.handle();

    let file_menu = SubmenuBuilder::new(handle, "File")
        .item(
            &MenuItemBuilder::with_id("new_session", "New Session")
                .accelerator("CmdOrCtrl+N")
                .build(handle)?,
        )
        .item(&PredefinedMenuItem::separator(handle)?)
        .item(
            &MenuItemBuilder::with_id("exit", "Exit")
                .accelerator("CmdOrCtrl+Q")
                .build(handle)?,
        )
        .build()?;

    let edit_menu = SubmenuBuilder::new(handle, "Edit")
        .item(
            &MenuItemBuilder::with_id("undo", "Undo")
                .accelerator("CmdOrCtrl+Z")
                .build(handle)?,
        )
        .item(
            &MenuItemBuilder::with_id("redo", "Redo")
                .accelerator("CmdOrCtrl+Shift+Z")
                .build(handle)?,
        )
        .item(&PredefinedMenuItem::separator(handle)?)
        .item(&PredefinedMenuItem::copy(handle, Some("Copy"))?)
        .item(&PredefinedMenuItem::paste(handle, Some("Paste"))?)
        .item(&PredefinedMenuItem::select_all(handle, Some("Select All"))?)
        .build()?;

    let view_menu = SubmenuBuilder::new(handle, "View")
        .item(&MenuItemBuilder::with_id("toggle_devtools", "Toggle DevTools").build(handle)?)
        .item(
            &MenuItemBuilder::with_id("reload", "Reload")
                .accelerator("CmdOrCtrl+R")
                .build(handle)?,
        )
        .item(&PredefinedMenuItem::separator(handle)?)
        .build()?;

    let window_menu = SubmenuBuilder::new(handle, "Window")
        .item(
            &MenuItemBuilder::with_id("minimize", "Minimize")
                .accelerator("CmdOrCtrl+M")
                .build(handle)?,
        )
        .item(&MenuItemBuilder::with_id("zoom", "Zoom").build(handle)?)
        .item(&PredefinedMenuItem::separator(handle)?)
        .build()?;

    let help_menu = SubmenuBuilder::new(handle, "Help")
        .item(&MenuItemBuilder::with_id("about", "About").build(handle)?)
        .item(&MenuItemBuilder::with_id("documentation", "Documentation").build(handle)?)
        .build()?;

    let menu = MenuBuilder::new(handle)
        .items(&[&file_menu, &edit_menu, &view_menu, &window_menu, &help_menu])
        .build()?;

    app.set_menu(menu)?;
    app.on_menu_event(|app_handle, event| match event.id().0.as_str() {
        "new_session" => emit_to_main(app_handle, "mantle://new-session", ""),
        "exit" => app_handle.exit(0),
        "undo" => emit_to_main(app_handle, "mantle://menu-edit", "undo"),
        "redo" => emit_to_main(app_handle, "mantle://menu-edit", "redo"),
        "toggle_devtools" => toggle_devtools(app_handle),
        "reload" => {
            if let Some(window) = app_handle.get_webview_window("main") {
                let _ = window.eval("window.location.reload()");
            }
        }
        "minimize" => {
            if let Some(window) = app_handle.get_webview_window("main") {
                let _ = window.minimize();
            }
        }
        "zoom" => toggle_maximize(app_handle),
        "about" => emit_to_main(app_handle, "mantle://about", "Rasputin Mantle v1.3"),
        "documentation" => {
            let _ =
                tauri_plugin_opener::open_url("https://github.com/rasputin/mantle", None::<&str>);
        }
        _ => {}
    });

    Ok(())
}

fn emit_to_main(app_handle: &tauri::AppHandle, event: &str, payload: &str) {
    if let Some(window) = app_handle.get_webview_window("main") {
        let _ = window.emit(event, payload);
    }
}

fn toggle_devtools(app_handle: &tauri::AppHandle) {
    if let Some(window) = app_handle.get_webview_window("main") {
        if window.is_devtools_open() {
            window.close_devtools();
        } else {
            window.open_devtools();
        }
    }
}

fn toggle_maximize(app_handle: &tauri::AppHandle) {
    if let Some(window) = app_handle.get_webview_window("main") {
        let is_maximized = window.is_maximized().unwrap_or(false);
        if is_maximized {
            let _ = window.unmaximize();
        } else {
            let _ = window.maximize();
        }
    }
}
