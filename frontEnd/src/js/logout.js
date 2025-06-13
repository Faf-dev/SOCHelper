document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (token) {
        const logoutButton = document.getElementById("logout-btn");

        if (logoutButton) {
            logoutButton.addEventListener("click", async () => {
                if (confirm("Êtes-vous sûr de vouloir vous déconnecter ?")) {
                    const res = await fetch("http://localhost:5000/api/auth/logout", {
                    method: "POST",
                    headers: { "Authorization": "Bearer " + token }
                });

                if (res.ok) {
                    localStorage.clear();
                    window.location.href = "login.html";
                }
            }
        });
    }
}
});
