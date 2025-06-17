document.addEventListener("DOMContentLoaded", () => {
  const uploadArea = document.getElementById("uploadArea");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const serverSelect = document.getElementById("server-filter");
  const selectedFile = document.getElementById("selectedFile");
  const fileName = document.getElementById("fileName");
  const token = sessionStorage.getItem("token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  let isFileDialogOpen = false;
  let currentFilePath = null;

  // Affichage du fichier sélectionné
  function displaySelectedFile(filePath) {
    currentFilePath = filePath;
    
    // Cacher la zone d'upload et afficher la zone de fichier sélectionné
    uploadArea.style.display = "none";
    if (selectedFile) selectedFile.style.display = "block";
    analyzeBtn.classList.add("show");
    if (fileName) fileName.textContent = filePath;
  }

  // Suppression du fichier
  function clearSelectedFile() {
    currentFilePath = null;
    uploadArea.style.display = "block";
    if (selectedFile) selectedFile.style.display = "none";
    analyzeBtn.classList.remove("show");
  }

  // Gestion du clic sur la zone d'upload
  uploadArea.addEventListener("click", async () => {
    if (isFileDialogOpen) return;
    isFileDialogOpen = true;

    try {
      const filePaths = await window.electron.openFile();
      if (filePaths && filePaths.length > 0) {
        displaySelectedFile(filePaths[0]);
      }
    } catch (error) {
      console.error("Erreur lors de l'ouverture du fichier :", error);
      alert("Une erreur est survenue lors de l'ouverture du fichier. Veuillez réessayer.");
    } finally {
      isFileDialogOpen = false;
    }
  });
  
  // Prévenir le comportement par défaut pour tous les événements de drag
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  // Gérer le drop du fichier
  uploadArea.addEventListener('drop', handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      const filePath = files[0].path;
      displaySelectedFile(filePath);
    }
  }

  // Suppression du fichier
  document.getElementById("removeFile").addEventListener("click", clearSelectedFile);

  // Lancement de l'analyse - A inclure
  analyzeBtn.addEventListener("click", async () => {
    if (!currentFilePath) {
      alert("Aucun fichier sélectionné");
      return;
    }

    if (!serverSelect.value) {
      alert("Veuillez sélectionner votre type de serveur");
      serverSelect.focus();
      return;
    }

    const formData = new FormData();
    formData.append("server", serverSelect.value);
    formData.append("chemin", currentFilePath);

    try {
      const res = await fetch("http://localhost:5000/api/settings/", {
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