#!/bin/bash
# Launch the SweetyAI Tauri desktop window (Linux).
cd "$(dirname "$0")"

# WebKitGTK DMABUF renderer crashes on Wayland for some GPU drivers; the app
# also sets this internally, but exported here as a belt-and-braces fallback.
export WEBKIT_DISABLE_DMABUF_RENDERER="${WEBKIT_DISABLE_DMABUF_RENDERER:-1}"

BIN=./src/target/debug/sweetyai_ui
if [ ! -x "$BIN" ]; then
  echo "[SweetyAI UI] Binary not found - building first..."
  (cd src && ~/.cargo/bin/cargo build) || exit 1
fi

exec "$BIN" "$@"
