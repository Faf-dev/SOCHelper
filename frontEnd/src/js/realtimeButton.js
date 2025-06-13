class RealtimeButton {
  constructor() {
    this.pollingInterval = null;
    this.isRealTimeActive = false;
    this.lastUpdateTime = null;
  }

  start() {
    if (this.isRealTimeActive) return;
    
    this.fetchNewData();
    this.pollingInterval = setInterval(() => this.fetchNewData(), 1000); // Scan toutes les secondes
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

  async fetchNewData() {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
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
          if (currentPage.includes('dashboard') || currentPage.includes('event')) {
            this.addNewEventsToTop(data);
          } else if (currentPage.includes('alert')) {
            this.addNewAlertsToTop(data);
          }
          
          this.lastUpdateTime = new Date().toISOString();
        }
      }
    } catch (err) {
      console.error("Erreur lors de la récupération des données temps réel :", err);
    }
  }

  addNewEventsToTop(events) {
    const tbody = document.querySelector(".log-table tbody");
    
    events.reverse().forEach(event => {
      const existingRow = tbody.querySelector(`[data-event-id="${event.evenement_id}"]`);
      if (existingRow) return;

      let date = "", heure = "";
      if (event.created_at) {
        const parts = event.created_at.split("T");
        date = parts[0];
        if (parts[1]) {
          heure = parts[1].split(".")[0];
        }
      }

      const tr = document.createElement("tr");
      tr.setAttribute("data-event-id", event.evenement_id);
      tr.innerHTML = `
        <td>${date}</td>
        <td>${heure}</td>
        <td>${event.ip_source}</td>
        <td>${event.type_evenement}</td>
        <td>${event.url_cible || ''}</td>
        <td><button class="btn_delete" data-type="event" data-id="${event.evenement_id}"><i class="bi bi-trash3"></i></button></td>
      `;
      
      // Ajouter en haut
      tbody.insertBefore(tr, tbody.firstChild);
    });
  }

  addNewAlertsToTop(alerts) {
    const tbody = document.querySelector(".log-table tbody");
    
    alerts.reverse().forEach(alert => {
      const existingRow = tbody.querySelector(`[data-alert-id="${alert.alerte_id}"]`);
      if (existingRow) return;

      let date = "", heure = "";
      if (alert.created_at) {
        const parts = alert.created_at.split("T");
        date = parts[0];
        if (parts[1]) {
          heure = parts[1].split(".")[0];
        }
      }

      const tr = document.createElement("tr");
      tr.setAttribute("data-alert-id", alert.alerte_id);
      tr.innerHTML = `
        <td>${date}</td>
        <td>${heure}</td>
        <td>${alert.ip_source}</td>
        <td>${alert.type_evenement}</td>
        <td>${alert.url_cible}</td>
        <td><button class="btn_delete" data-type="alert" data-id="${alert.alerte_id}"><i class="bi bi-trash3"></i></button></td>
      `;
      
      tbody.insertBefore(tr, tbody.firstChild);
    });
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

const realtimeButton = new RealtimeButton();

document.addEventListener("DOMContentLoaded", () => {
  realtimeButton.init();
});
