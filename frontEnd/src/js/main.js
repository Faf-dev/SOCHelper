const { app, BrowserWindow, ipcMain, dialog, Notification } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const NotificationManager = require("./notificationManager");

const notificationManager = new NotificationManager();

let backendProcess;


function startBackend() {
  const isDev = !app.isPackaged;
  const exePath = isDev
    ? path.join(__dirname, "../../dist/run.exe")
    : path.join(process.resourcesPath, "run.exe");

  console.log("Tentative de démarrage du backend:", exePath);

  backendProcess = spawn(exePath, [], {
    detached: false,
    stdio: ["ignore", "pipe", "pipe"]
  });

  // Handler unique pour les logs normaux ET les messages JSON
  backendProcess.stdout.on("data", (data) => {
    const output = data.toString();
    console.log("Backend output:", output);
    
    // Envoie les logs à la fenêtre principale
    if (BrowserWindow.getAllWindows().length > 0) {
      BrowserWindow.getAllWindows()[0].webContents.send("backend-log", output);
    }
    
    // Essaie de parser chaque ligne comme JSON
    const lines = output.split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const message = JSON.parse(line.trim());
          console.log("Message JSON reçu:", message);
          
          if (message.type === "sqlInjection") {
            const { ip, date, heure } = message.data;
            console.log("Déclenchement notification SQL injection pour:", ip);
            notificationManager.showSQLInjectionAlert(ip, date, heure);
          } else if (message.type === "brutForce") {
            const { ip, attempts, date, heure } = message.data;
            notificationManager.showBruteForceAlert(ip, attempts, date, heure);
          }
        } catch (error) {
          console.error("Erreur de parsing JSON:", error);
        }
      }
    }
  });
  
  backendProcess.stderr.on("data", (data) => {
    console.error("Backend stderr:", data.toString());
    if (BrowserWindow.getAllWindows().length > 0) {
      BrowserWindow.getAllWindows()[0].webContents.send("backend-log", data.toString());
    }
  });
  
  backendProcess.on("error", (error) => {
    console.error("Erreur lors du démarrage du backend:", error);
  });
  
  backendProcess.on("close", (code) => {
    console.log("Backend fermé avec le code:", code);
    backendProcess = null; // Nettoyer la référence
  });

  backendProcess.on("exit", (code, signal) => {
    console.log(`Backend terminé avec le code ${code} et le signal ${signal}`);
    backendProcess = null; // Nettoyer la référence
  });
}



app.whenReady().then(() => {
  app.setAppUserModelId("com.sochelper.app");
  startBackend();
  createWindow();
});


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

/* Gestionnaire IPC */


// Gestionnaire IPC pour drag & drop
ipcMain.handle("dialog:openFile", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openFile"], // Permet de choisir un fichier
    filters: [{ name: "Logs", extensions: ["log"] }], // Filtre pour ne montrer que les fichiers .log
  });
  return result.filePaths; // Renvoie le chemin du fichier choisi
});

// Gestionnaire IPC pour les notifications SQL injection
ipcMain.handle("security:sqlInjection", async (event, data) => {
  const { ip, date, heure } = data;
  console.log("Message reçu via IPC:", data);
  notificationManager.showSQLInjectionAlert(ip, date, heure);
  console.log("Notification SQL injection envoyée pour l'IP:", ip);
  return { success: true };
});

// Gestionnaire IPC pour les notifications brute force
ipcMain.handle("security:brutForce", async (event, data) => {
  const { ip, attempts, date, heure } = data;
  console.log("Message reçu via IPC:", data);
  notificationManager.showBruteForceAlert(ip, attempts, date, heure);
  console.log("Notification brute force envoyée pour l'IP:", ip);
  return { success: true };
});

// Quitter quand toutes les fenêtres sont fermées (uniquement sur macOS)
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on("window-all-closed", () => {
  // Fermer le backend avant de quitter l'application
  if (backendProcess && !backendProcess.killed) {
    console.log("Fermeture du backend...");
    backendProcess.kill('SIGTERM'); // Essaie un arrêt propre
    
    // Si le processus ne se ferme pas dans 3 secondes, le forcer
    setTimeout(() => {
      if (backendProcess && !backendProcess.killed) {
        console.log("Forçage de la fermeture du backend...");
        backendProcess.kill('SIGKILL');
      }
    }, 3000);
  }
  
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// Gestionnaire pour fermeture propre du backend avant quit
app.on("before-quit", (event) => {
  if (backendProcess && !backendProcess.killed) {
    console.log("Arrêt du backend avant fermeture de l'application...");
    event.preventDefault(); // Empêche la fermeture immédiate
    
    backendProcess.kill('SIGTERM');
    
    // Attendre que le processus se ferme ou le forcer après 3 secondes
    const forceQuitTimeout = setTimeout(() => {
      if (backendProcess && !backendProcess.killed) {
        console.log("Forçage de la fermeture du backend...");
        backendProcess.kill('SIGKILL');
      }
      app.quit(); // Fermer l'app après avoir forcé l'arrêt
    }, 3000);
    
    // Si le processus se ferme proprement, annuler le timeout et quitter
    backendProcess.on('close', () => {
      clearTimeout(forceQuitTimeout);
      console.log("Backend fermé proprement");
      app.quit();
    });
  }
});
