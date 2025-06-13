document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("register-form");

  // Crée un élément pour afficher les messages d'erreur ou de succès
  const errorDiv = document.createElement("div");
  errorDiv.id = "register-message";
  errorDiv.style.marginBottom = "15px";
  errorDiv.style.textAlign = "center";

  form.prepend(errorDiv); // ajout du message d'erreur au dessus du formulaire

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorDiv.innerText = ""; // vider le message d'erreur avant chaque nouvelle tentative
    errorDiv.style.color = "inherit";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const res = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok) {
        errorDiv.innerText = "Inscription réussie ! Redirection...";
        errorDiv.style.color = "white";

        setTimeout(() => {
          window.location.href = "login.html";
        }, 1000); // redirection après 1s

      } else {
        errorDiv.innerText = data.msg || "Erreur lors de l'inscription";
        errorDiv.style.color = "red";
      }
    } catch (err) {
      errorDiv.innerText = "Erreur de connexion au serveur.";
      errorDiv.style.color = "red";
      console.error(err);
    }
  });
});
