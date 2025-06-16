const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  openFile: () => ipcRenderer.invoke("dialog:openFile"), // méthode pour ouvrir la boîte de dialogue
});
