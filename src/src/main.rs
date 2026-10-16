// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

fn main() {
  // WebKitGTK's DMABUF renderer crashes with "Error 71 (Protocol error)" on
  // Wayland compositors for some GPU/driver combinations. Fall back to the
  // software-safe path unless the user has explicitly overridden it.
  #[cfg(target_os = "linux")]
  if std::env::var_os("WEBKIT_DISABLE_DMABUF_RENDERER").is_none() {
    std::env::set_var("WEBKIT_DISABLE_DMABUF_RENDERER", "1");
  }

  tauri::Builder::default()
    .setup(|app| {
      // Force Windows to completely remove the native window shadow and border box
      if let Some(window) = app.get_webview_window("main") {
        let _ = window.set_shadow(false);
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}