const { app, BrowserWindow, session, ipcMain } = require('electron');
const path = require('path');

// Disable GPU shader disk cache and grant media permissions automatically
app.commandLine.appendSwitch('disable-gpu-shader-disk-cache');
app.commandLine.appendSwitch('use-fake-ui-for-media-stream');
app.commandLine.appendSwitch('enable-features', 'WebRtcHideLocalIpsWithMdns');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 520,
    height: 540,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: false,
    hasShadow: false,
    icon: path.join(__dirname, 'assets', 'logo.png'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false, // Enables ultra-fast direct IPC & media access
      webSecurity: false
    }
  });

  // Automatically approve all audio/mic permission requests
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(true);
  });
  session.defaultSession.setPermissionCheckHandler((webContents, permission) => {
    return true;
  });

  mainWindow.setAlwaysOnTop(true, 'screen-saver');
  mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
}

// ----------------------------------------------------
// Smooth Real-Time Corner-to-Corner Window Dragging
// ----------------------------------------------------
let dragOffset = { x: 0, y: 0 };

ipcMain.on('drag-start', (event, { screenX, screenY }) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) {
    const [winX, winY] = win.getPosition();
    dragOffset = { x: screenX - winX, y: screenY - winY };
  }
});

ipcMain.on('drag-move', (event, { screenX, screenY }) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) {
    win.setPosition(Math.round(screenX - dragOffset.x), Math.round(screenY - dragOffset.y));
  }
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
