let eventsPagination;

document.addEventListener("DOMContentLoaded", () => {
  eventsPagination = new SimplePagination('http://localhost:5000/api/event/', 10);
  window.globalPagination = eventsPagination;
  eventsPagination.init();
});

function updateEventsTable(events) {
  const tbody = document.querySelector(".log-table tbody");
  
  events.forEach(event => {
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
    tbody.insertBefore(tr, tbody.firstChild);
  });
  
  if (events.length > 0 && window.globalPagination) {
    setTimeout(() => window.globalPagination.refreshPagination(), 100);
  }
}
