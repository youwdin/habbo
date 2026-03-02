const { app, BrowserWindow } = require('electron');

// HavanaWeb runs on port 8080 — we load play.html from it directly.
// Make sure Havana-Web.jar is running before launching this app.
const HAVANA_WEB = 'http://127.0.0.1:8080';

function createWindow() {
  const win = new BrowserWindow({
    width:  1280,
    height: 820,
    minWidth: 800,
    minHeight: 600,
    title: 'Beebo Hotel',
    backgroundColor: '#1a1a1a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,   // needed for cross-origin SWF/WASM requests
    },
  });

  // play.html is served by HavanaWeb and uses Ruffle to load Habbo.swf
  win.loadURL(`${HAVANA_WEB}/play.html`);

  // uncomment to open DevTools:
  // win.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
