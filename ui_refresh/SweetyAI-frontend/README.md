# SweetyAI — Windows top-edge frontend

A SweetyAI-branded Tauri 2 desktop frontend built around a compact top-edge island interaction model.

## UI

- Compact top-edge assistant island
- Smooth expand/collapse transition
- SweetyAI character mark with original visuals
- Chat-first expanded workspace
- Quick-start cards
- Thinking state and online/offline indicator
- New-chat and collapse controls
- File action placeholder ready for backend integration
- Local Python backend at `127.0.0.1:8765`

## Run

```powershell
npm install
npm run tauri:dev
```

Start the existing SweetyAI Python backend separately:

```powershell
.\.venv\Scripts\python.exe server.py
```
