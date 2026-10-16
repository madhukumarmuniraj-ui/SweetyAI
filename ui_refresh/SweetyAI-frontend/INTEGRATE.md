# Integrate with your existing C:\SweetyAI

1. Copy `server.py` into `C:\SweetyAI\server.py`.
2. Start it from PowerShell:

```powershell
cd C:\SweetyAI
.\.venv\Scripts\python.exe server.py
```

3. In the frontend project run:

```powershell
npm install
npm run tauri:dev
```

The frontend calls:

`POST http://127.0.0.1:8765/chat`

with:

```json
{"message":"Hello"}
```

and expects:

```json
{"ok":true,"content":"..."}
```

The API key/model credentials remain in your Python process instead of browser TypeScript.
