class LogPathDisplay {
  constructor() {
    this.logPathDiv = document.querySelector(".log-path");
  }

  async updateLogPathDisplay() {
    const logId = localStorage.getItem("currentLogId");
    
    if (!logId) {
      this.logPathDiv.innerHTML = 'Log: <code>Aucun fichier log sélectionné</code> |';
      return;
    }

    try {
      const token = sessionStorage.getItem("token");
      const res = await fetch(`http://localhost:5000/api/settings/logs/${logId}`, {
        headers: { "Authorization": "Bearer " + token }
      });
      
      if (res.ok) {
        const logInfo = await res.json();
        const serverType = logInfo.type_log.toUpperCase();
        this.logPathDiv.innerHTML = `Log: <code>${logInfo.chemin}</code> | ${serverType}`;
        console.log("En-tête mis à jour :", logInfo.chemin, serverType);
      } else {
        console.error("Erreur API :", res.status);
        this.logPathDiv.innerHTML = 'Log: <code>Aucun fichier log sélectionné</code> |';
      }
    } catch (err) {
      console.error("Erreur lors de la récupération du log :", err);
      this.logPathDiv.innerHTML = 'Log: <code>Aucun fichier log sélectionné</code> |';
    }
  }

  // Méthode pour forcer la mise à jour (utile si on change de fichier log)
  refresh() {
    this.updateLogPathDisplay();
  }
}

// Initialisation au chargement de la page
document.addEventListener("DOMContentLoaded", () => {
  const logPathDisplay = new LogPathDisplay();
  logPathDisplay.updateLogPathDisplay();
  
  // accessible globalement si besoin
  window.logPathDisplay = logPathDisplay;
});
