document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  try {
    const tbody = document.querySelector(".log-table tbody");
    tbody.addEventListener("click", async (e) => {
    if (e.target.closest(".btn_delete")) {
        const btn = e.target.closest(".btn_delete");
        const itemId = btn.getAttribute("data-id");
        const itemType = btn.getAttribute("data-type");
        let apiRoute = "";
        let confirmMessage = "";

        if (itemType === "event") {
          apiRoute = `http://localhost:5000/api/event/${itemId}`;
          confirmMessage = "Supprimer cet événement ?";
        } else if (itemType === "alert") {
            apiRoute = `http://localhost:5000/api/alert/${itemId}`;
            confirmMessage = "Supprimer cette alerte ?";
        } else {
          console.error("Type d'élément non reconnu :", itemType);
          return;
        }
    
        if (confirm(confirmMessage)) {
          const res = await fetch(apiRoute, {
          method: "DELETE",
          headers: {
            "Authorization": "Bearer " + token
          }
        });
        if (res.ok) {
          if (window.globalPagination) {
            window.globalPagination.refreshPagination();
          }
          btn.closest("tr").remove();
        } else {
          alert("Erreur lors de la suppression !");
        }
      }
    }
}
    );
  } catch (err) {
    console.error("Erreur :", err);
  }                                 
});
