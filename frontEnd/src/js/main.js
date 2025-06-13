const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow () {
  const win = new BrowserWindow({
    width: 1540,
    height: 870,
    webPreferences: {
      nodeIntegration: true
    }
  });
  const htmlPath = path.join(__dirname, "..", "/html/login.html");
  win.loadFile(htmlPath);
}

app.whenReady().then(() => {
  createWindow();
});

  // Quitter quand toutes les fenêtres sont fermées (uniquement sur macOS)
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on("window-all-closed", () => {
if (process.platform !== "darwin") {
  app.quit();
  }
});
