document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch("http://localhost:5000/api/auth/user", {
      headers: {
        "Authorization": "Bearer " + token
      }
    });
    if (res.ok) {
      const data = await res.json();
      document.querySelector(".user-info strong").textContent = data.email;
    } else {
      document.querySelector(".user-info strong").textContent = "Non connecté";
    }
  } catch (err) {
    console.error("Erreur lors de la récupération de l'email :", err);
  }
});
