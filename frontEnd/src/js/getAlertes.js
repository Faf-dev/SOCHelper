let alertsPagination;

document.addEventListener("DOMContentLoaded", () => {
  alertsPagination = new SimplePagination('http://localhost:5000/api/alert/', 5);
  window.globalPagination = alertsPagination;
  alertsPagination.init();
});

function updateAlertsTable(alerts) {
  const tbody = document.querySelector(".log-table tbody");
  
  alerts.forEach(alert => {
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
      <td>${alert.status_code !== null ? alert.status_code : 'N/A'}</td>
      <td>${alert.url_cible}</td>
      <td><button class="btn_delete" data-type="alert" data-id="${alert.alerte_id}"><i class="bi bi-trash3"></i></button></td>
    `;
    tbody.insertBefore(tr, tbody.firstChild);
  });
  
  if (alerts.length > 0 && window.globalPagination) {
    setTimeout(() => window.globalPagination.refreshPagination(), 100);
  }
}
