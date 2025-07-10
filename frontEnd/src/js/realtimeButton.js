class RealtimeButton {
  constructor() {
    this.pollingInterval = null;
    this.isRealTimeActive = false;
    this.lastUpdateTime = null;
    this.lastEventId = null;
  }

  start() {
    if (this.isRealTimeActive) return;
    
    // UNE SEULE analyse au démarrage
    this.triggerLogAnalysis();
    
    // Puis polling pour les nouvelles données seulement
    this.pollingInterval = setInterval(() => this.fetchNewData(), 2000);
    this.isRealTimeActive = true;
    this.updateButtonState();
    
    console.log('Temps réel démarré');
  }

  stop() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    this.isRealTimeActive = false;
    this.updateButtonState();
    
    console.log('Temps réel arrêté');
  }

  toggle() {
    if (this.isRealTimeActive) {
      this.stop();
    } else {
      this.start();
    }
  }

    async triggerLogAnalysis() {
    const token = sessionStorage.getItem("token");
    if (!token) return;

    const btn = document.getElementById('realtime-toggle');
    const fichier_log_id = btn.dataset.logId;  
    if (!fichier_log_id) return;

    try {
      const res = await fetch('http://localhost:5000/api/event/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ fichier_log_id })
      });
      if (!res.ok) {
        console.error('Analyse failed:', await res.text());
      }
    } catch (err) {
      console.error('Erreur triggerLogAnalysis:', err);
    }
  }

  async fetchNewData() {
    const token = sessionStorage.getItem("token");
    if (!token) {
    window.location.href = "login.html";
    return;
    }

    try {
      // Vérifier s'il y a de nouvelles données dans le fichier de log
      // en déclenchant une analyse qui ne traitera que les nouvelles lignes
      await this.triggerLogAnalysis();
      
      // Rafraîchir la pagination pour afficher les nouveaux événements
      if (window.globalPagination) {
        window.globalPagination.refreshPagination();
      }
      
      this.lastUpdateTime = new Date().toISOString();
      
    } catch (err) {
      console.error("Erreur lors de la récupération des données temps réel :", err);
    }
  }

  updateButtonState() {
    const button = document.getElementById('realtime-toggle');
    const statusDot = document.querySelector('.status .dot');
    
    if (this.isRealTimeActive) {
      if (button) button.textContent = 'Stop';
      if (statusDot) {
        statusDot.classList.add('active');
        statusDot.classList.remove('inactive');
      }
    } else {
      if (button) button.textContent = 'Start';
      if (statusDot) {
        statusDot.classList.add('inactive');
        statusDot.classList.remove('active');
      }
    }
  }

  init() {
    const realtimeButton = document.getElementById('realtime-toggle');
    if (realtimeButton) {
      realtimeButton.addEventListener('click', () => this.toggle());
    }
    this.updateButtonState();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("realtime-toggle");
  if (!btn) return; // protection
  // injecte l'ID du log uploadé depuis la page settings
  btn.dataset.logId = localStorage.getItem("currentLogId") || "";
  const rt = new RealtimeButton();
  rt.init();
});
