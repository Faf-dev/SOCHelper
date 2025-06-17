document.addEventListener("DOMContentLoaded", () => {
    const token = sessionStorage.getItem("token");
    if (!token) {
    window.location.href = "login.html";
    return;
    } else {
        const logoutButton = document.getElementById("logout-btn");

        if (logoutButton) {
            logoutButton.addEventListener("click", async () => {
                if (confirm("Êtes-vous sûr de vouloir vous déconnecter ?")) {
                    const res = await fetch("http://localhost:5000/api/auth/logout", {
                    method: "POST",
                    headers: { "Authorization": "Bearer " + token }
                });

                if (res.ok) {
                    sessionStorage.clear();
                    window.location.href = "login.html";
                }
            }
        });
      }
    }
});
