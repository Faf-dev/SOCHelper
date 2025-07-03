class RealtimeButton {
  constructor() {
    this.pollingInterval = null;
    this.isRealTimeActive = false;
    this.lastUpdateTime = null;
    this.lastEventId = null;
  }

  start() {
    if (this.isRealTimeActive) return;
    
    this.triggerLogAnalysis();
    this.fetchNewData();
    this.pollingInterval = setInterval(() => this.fetchNewData(), 1000); // 2 secondes au lieu de 500ms
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
      await this.triggerLogAnalysis();
      
      const currentPage = window.location.pathname;
      let url;
      
      if (currentPage.includes('dashboard') || currentPage.includes('event')) {
        url = this.lastUpdateTime 
          ? `http://localhost:5000/api/event/?since=${this.lastUpdateTime}`
          : "http://localhost:5000/api/event";
      } else if (currentPage.includes('alert')) {
        url = this.lastUpdateTime 
          ? `http://localhost:5000/api/alert/?since=${this.lastUpdateTime}`
          : "http://localhost:5000/api/alert";
      } else {
        return;
      }

      const res = await fetch(url, {
        headers: { "Authorization": "Bearer " + token }
      });

      if (res.status === 401) {
        localStorage.clear();
        alert("Session expirée. Veuillez vous reconnecter.");
        window.location.href = "login.html";
        return;
      }

      if (res.ok) {
        const data = await res.json();
        
        if (data.length > 0) {
          // Rafraîchit la pagination sur la page courante pour maintenir la cohérence
          if (window.globalPagination) {
            window.globalPagination.refreshPagination();
          }
          
          this.lastUpdateTime = new Date().toISOString();
        }
      }
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
