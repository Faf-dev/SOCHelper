document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");

  // Crée un élément pour afficher les messages d'erreur ou de succès
  const errorDiv = document.createElement("div");
  errorDiv.id = "login-message";
  errorDiv.style.marginBottom = "15px";

  form.prepend(errorDiv); // ajout du message d'erreur au dessus du formulaire

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorDiv.innerText = ""; // vider le message d'erreur avant chaque nouvelle tentative
    errorDiv.style.color = "inherit";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const res = await fetch("http://localhost:5000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok) {
        errorDiv.innerText = "Connexion réussie ! Redirection...";
        errorDiv.style.color = "white";
        sessionStorage.setItem("token", data.access_token); // stockage du token JWT en local
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 1000); // redirection après 1s vers le dashboard
      } else {
        errorDiv.innerText = data.msg || "Trop de tentatives échouées. Veuillez réessayer plus tard.";
        errorDiv.style.color = "red";
      }
    } catch (err) {
      errorDiv.innerText = "Erreur lors de la connexion au serveur.";
      errorDiv.style.color = "red";
      console.error(err);
    }
  });
});
