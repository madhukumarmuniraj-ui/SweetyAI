const { contextBridge, ipcRenderer } = require('electron');

const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('electronAPI', {
    sendMessage: (msg) => ipcRenderer.invoke('ai-chat-message', msg)
});
contextBridge.exposeInMainWorld('sweety', {
  getWindowRole: () => ipcRenderer.invoke('window-role'),
  openPanel: (mode = 'menu') => ipcRenderer.send('sweety-open-panel', mode),
  togglePanel: (mode = 'menu') => ipcRenderer.send('sweety-toggle-panel', mode),
  closePanel: () => ipcRenderer.send('sweety-close-panel'),
  setPanelMode: (mode) => ipcRenderer.send('panel-set-mode', mode),
  repositionPanel: () => ipcRenderer.send('panel-reposition'),
  setAlwaysOnTop: (enabled) => ipcRenderer.invoke('set-always-on-top', enabled),
  captureScreen: () => ipcRenderer.invoke('capture-screen'),
  startDrag: (screenX, screenY) => ipcRenderer.send('drag-start', { screenX, screenY }),
  moveDrag: (screenX, screenY) => ipcRenderer.send('drag-move', { screenX, screenY }),
  endDrag: () => ipcRenderer.send('drag-end'),
  startNativeMicRecording: () => ipcRenderer.invoke('start-native-mic-recording'),
  stopNativeMicRecording: () => ipcRenderer.invoke('stop-native-mic-recording'),
  setSweetyState: (state) => ipcRenderer.send('sweety-set-state', state),
  triggerEmote: (emote) => ipcRenderer.send('sweety-trigger-emote', emote),
  setPiste: (piste) => ipcRenderer.send('sweety-set-piste', piste),
  onSweetyState: (callback) => {
    const listener = (_event, state) => callback(state);
    ipcRenderer.on('sweety-state', listener);
    return () => ipcRenderer.removeListener('sweety-state', listener);
  },
  onSweetyEmote: (callback) => {
    const listener = (_event, emote) => callback(emote);
    ipcRenderer.on('sweety-emote', listener);
    return () => ipcRenderer.removeListener('sweety-emote', listener);
  },
  onSweetyPiste: (callback) => {
    const listener = (_event, piste) => callback(piste);
    ipcRenderer.on('sweety-piste', listener);
    return () => ipcRenderer.removeListener('sweety-piste', listener);
  },
  onPanelMode: (callback) => {
    const listener = (_event, mode) => callback(mode);
    ipcRenderer.on('panel-mode', listener);
    return () => ipcRenderer.removeListener('panel-mode', listener);
  },
  onNotificationPill: (callback) => {
    const listener = (_event, notification) => callback(notification);
    ipcRenderer.on('sweety-notification', listener);
    return () => ipcRenderer.removeListener('sweety-notification', listener);
  },
  sendNotificationPill: (notification) => ipcRenderer.send('sweety-trigger-notification', notification),
});
