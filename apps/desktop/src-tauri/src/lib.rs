mod menu;
mod single_instance;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_updater::Builder::new().build());

    single_instance::attach(builder)
        .invoke_handler(tauri::generate_handler![
            single_instance::focus_main_window,
            single_instance::navigate_existing_window,
        ])
        .setup(|app| {
            menu::install(app)?;
            single_instance::navigate_to_configured_web_url(app.handle());
            Ok(())
        })
        .run(tauri::generate_context!("../tauri.conf.json"))
        .expect("error while running tauri application");
}
