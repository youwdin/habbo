const { app, BrowserWindow, protocol } = require('electron');
const path = require('path');
const http  = require('http');
const fs    = require('fs');
const url   = require('url');

const WWW_DIR = path.join(__dirname, '../Havana/tools/www');
const PORT    = 8080;

const MIME = {
  '.html': 'text/html',
  '.js':   'application/javascript',
  '.css':  'text/css',
  '.swf':  'application/x-shockwave-flash',
  '.dcr':  'application/x-director',
  '.wasm': 'application/wasm',
  '.xml':  'application/xml',
  '.json': 'application/json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.gif':  'image/gif',
  '.ico':  'image/x-icon',
  '.svg':  'image/svg+xml',
  '.ttf':  'font/ttf',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
};

// Minimal local file server serving www directory
function startServer(cb) {
  const server = http.createServer((req, res) => {
    let filePath = path.join(WWW_DIR, url.parse(req.url).pathname);

    // default to index
    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
      filePath = path.join(filePath, 'index.html');
    }

    const ext  = path.extname(filePath).toLowerCase();
    const mime = MIME[ext] || 'application/octet-stream';

    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404); res.end('Not found');
      } else {
        res.writeHead(200, {
          'Content-Type': mime,
          'Access-Control-Allow-Origin': '*',
        });
        res.end(data);
      }
    });
  });

  server.listen(PORT, '127.0.0.1', () => cb(server));
}

function createWindow() {
  const win = new BrowserWindow({
    width:  1280,
    height: 820,
    minWidth: 800,
    minHeight: 600,
    title: 'Ruffle — Habbo.swf',
    backgroundColor: '#1a1a1a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      // allow the Claude API fetch from renderer
      webSecurity: false,
    },
  });

  win.loadURL(`http://127.0.0.1:${PORT}/play.html`);

  // uncomment to open DevTools:
  // win.webContents.openDevTools();
}

app.whenReady().then(() => {
  startServer(() => {
    createWindow();
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
