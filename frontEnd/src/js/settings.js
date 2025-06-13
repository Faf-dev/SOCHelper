document.addEventListener("DOMContentLoaded", () => {
  const uploadArea = document.getElementById("uploadArea");
  const fileInput = document.getElementById("fileInput");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const serverSelect = document.getElementById("server-filter");
  const token = localStorage.getItem("token");
  if (!token) return;

  let currentFile = null;
  let currentFilePath = null;

  // Affichage du fichier sélectionné
  function displaySelectedFile(file) {
    currentFile = file;
    currentFilePath = file.path;
    uploadArea.style.display = "none";
    analyzeBtn.classList.add("show");
  }

  // Suppression du fichier
  function clearSelectedFile() {
    currentFile = null;
    uploadArea.style.display = "block";
    analyzeBtn.classList.remove("show");
    fileInput.value = "";
  }

  // Gestion du drag & drop
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("dragover");
  });

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("dragover");
  });

  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("dragover");

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      displaySelectedFile(file);
    }
  });

  // Clic sur la zone d'upload
  uploadArea.addEventListener("click", () => {
    fileInput.click();
  });

  // Sélection de fichier via l'input
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      displaySelectedFile(file);
    }
  });

  // Suppression du fichier
  document.getElementById("removeFile").addEventListener("click", clearSelectedFile);

  // Lancement de l'analyse
  analyzeBtn.addEventListener("click", async () => {
    if (!currentFile) {
      alert("Aucun fichier sélectionné");
      return;
    }

    if (!serverSelect.value) {
      alert("Veuillez sélectionner votre type de serveur");
      serverSelect.focus();
      return;
    }

    // Prépare les données à envoyer
    const formData = new FormData();
    formData.append("server", serverSelect.value);
    formData.append("file", currentFile);
    formData.append("chemin", currentFilePath);

    try {
      // Envoie les données à l'API Flask
      const res = await fetch("http://localhost:5000/api/settings", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + token,
        },
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        alert("Analyse lancée avec succès !");
        console.log("Réponse de l'API :", data);
        window.location.href = "dashboard.html";
      } else {
        const error = await res.json();
        alert("Erreur lors de l'analyse : " + error.msg);
      }
    } catch (err) {
      console.error("Erreur lors de l'envoi à l'API :", err);
      alert("Une erreur est survenue. Veuillez réessayer.");
    }
  });
});
