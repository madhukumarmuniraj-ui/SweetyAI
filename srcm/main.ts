// Example in your Electron main file (e.g., main.js)
const panelWin = new BrowserWindow({
  width: 380,   // Set compact width matching the photo
  height: 220,  // Set compact height matching the photo
  frame: false,
  transparent: true,
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    preload: path.join(__dirname, 'preload.js')
  }
});