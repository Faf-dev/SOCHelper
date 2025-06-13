class SimplePagination {
  constructor(apiEndpoint, itemsPerPage = 5) {
    this.apiEndpoint = apiEndpoint;
    this.itemsPerPage = itemsPerPage;
    this.currentPage = 1;
    this.nextPageHasData = false;
  }

  async loadPage(page = 1) {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const res = await fetch(`${this.apiEndpoint}?page=${page}&per_page=${this.itemsPerPage}`, {
        headers: { "Authorization": "Bearer " + token }
      });

      if (res.status === 401) {
        this.handle401();
        return;
      }

      const data = await res.json();
      this.currentPage = page;
      
      // Afficher les données selon le type
      if (this.apiEndpoint.includes('event')) {
        this.displayEvents(data);
      } else if (this.apiEndpoint.includes('alert')) {
        this.displayAlerts(data);
      }

      // Vérifier la page suivante
      await this.checkNextPage(page);
      this.updatePaginationUI();

    } catch (err) {
      console.error("Erreur lors de la récupération des données :", err);
    }
  }

  async checkNextPage(currentPage) {
    const token = localStorage.getItem("token");
    try {
      const resNext = await fetch(`${this.apiEndpoint}?page=${currentPage + 1}&per_page=${this.itemsPerPage}`, {
        headers: { "Authorization": "Bearer " + token }
      });
      
      if (resNext.status === 401) {
        this.handle401();
        return;
      }
      
      const nextData = await resNext.json();
      this.nextPageHasData = nextData.length > 0;
    } catch (err) {
      this.nextPageHasData = false;
    }
  }

  displayEvents(events) {
    const tbody = document.querySelector(".log-table tbody");
    tbody.innerHTML = "";
    
    events.forEach(event => {
      const tr = document.createElement("tr");
      tr.setAttribute("data-event-id", event.evenement_id);
      
      let date = "", heure = "";
      if (event.created_at) {
        const parts = event.created_at.split("T");
        date = parts[0];
        if (parts[1]) {
          heure = parts[1].split(".")[0];
        }
      }

      tr.innerHTML = `
        <td>${date}</td>
        <td>${heure}</td>
        <td>${event.ip_source}</td>
        <td>${event.type_evenement}</td>
        <td>${event.url_cible || ''}</td>
        <td><button class="btn_delete" data-type="event" data-id="${event.evenement_id}"><i class="bi bi-trash3"></i></button></td>
      `;
      tbody.appendChild(tr);
    });
  }

  displayAlerts(alerts) {
    const tbody = document.querySelector(".log-table tbody");
    tbody.innerHTML = "";
    
    alerts.forEach(alert => {
      const tr = document.createElement("tr");
      tr.setAttribute("data-alert-id", alert.alerte_id);
    let date = "", heure = "";
    if (alert.created_at) {
      const parts = alert.created_at.split("T");
      date = parts[0];
      if (parts[1]) {
        heure = parts[1].split(".")[0]; // Enlever les millisecondes
      }
    }
      
      tr.innerHTML = `
        <td>${date}</td>
        <td>${heure}</td>
        <td>${alert.ip_source}</td>
        <td>${alert.type_evenement}</td>
        <td>${alert.url_cible}</td>
        <td><button class="btn_delete" data-type="alert" data-id="${alert.alerte_id}"><i class="bi bi-trash3"></i></button></td>
      `;
      tbody.appendChild(tr);
    });
  }

  updatePaginationUI() {
    const paginationContainer = document.getElementById("pagination");
    if (!paginationContainer) return;

    paginationContainer.innerHTML = `
      <button id="prevPage" ${this.currentPage === 1 ? "disabled" : ""}>⟵ Précédent</button>
      <span>Page ${this.currentPage}</span>
      <button id="nextPage" ${!this.nextPageHasData ? "disabled" : ""}>Suivant ⟶</button>
    `;

    document.getElementById("prevPage").onclick = () => {
      if (this.currentPage > 1) {
        this.loadPage(this.currentPage - 1);
      }
    };

    document.getElementById("nextPage").onclick = () => {
      if (this.nextPageHasData) {
        this.loadPage(this.currentPage + 1);
      }
    };
  }

  async refreshPagination() {
    this.loadPage(this.currentPage);
  }

  handle401() {
    localStorage.clear();
    alert("Session expirée. Veuillez vous reconnecter.");
    window.location.href = "login.html";
  }

  init() {
    this.loadPage(this.currentPage);
  }
}
