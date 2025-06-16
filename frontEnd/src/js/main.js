const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");

function createWindow () {
  const win = new BrowserWindow({
    width: 1540,
    height: 870,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"), // Charge preload.js
      nodeIntegration: false,
      contextIsolation: true,
    }
  });
  const htmlPath = path.join(__dirname, "..", "/html/login.html");
  win.loadFile(htmlPath);
}

app.whenReady().then(() => {
  createWindow();
});

ipcMain.handle("dialog:openFile", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openFile"], // Permet de choisir un fichier
    filters: [{ name: "Logs", extensions: ["log"] }], // Filtre pour ne montrer que les fichiers .log
  });
  return result.filePaths; // Renvoie le chemin du fichier choisi
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
