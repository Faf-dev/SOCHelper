document.addEventListener("DOMContentLoaded", () => {
  const uploadArea = document.getElementById("uploadArea");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const serverSelect = document.getElementById("server-filter");
  const selectedFile = document.getElementById("selectedFile");
  const fileName = document.getElementById("fileName");
  const token = sessionStorage.getItem("token");
  const filesList = document.getElementById("filesList");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  let isFileDialogOpen = false;
  let currentFilePath = null;
  let selectedLogId = localStorage.getItem("currentLogId") || null;

   // Charger les fichiers existants au chargement de la page
  loadExistingFiles();

  async function loadExistingFiles() {
    try {
      const res = await fetch("http://localhost:5000/api/settings/logs", {
        headers: { "Authorization": "Bearer " + token }
      });
      if (res.ok) {
        const files = await res.json();
        displayExistingFiles(files);
      } else {
      console.error("Erreur API :", res.status, await res.text());
      displayExistingFiles([]);
    }
    } catch (err) {
      console.error("Erreur lors du chargement des fichiers :", err);
      displayExistingFiles([]); // évite un crash si l'API est inaccessible
    }
  }

  function displayExistingFiles(files) {
    if (!filesList) {
     console.error("Élément filesList non trouvé");
     return;
   }
   
   // Vérifier que files est un tableau
   if (!Array.isArray(files)) {
     console.error("files n'est pas un tableau :", files);
     filesList.innerHTML = "<p>Erreur de format des données</p>";
     return;
   }
   
    filesList.innerHTML = "";
   
   if (files.length === 0) {
     filesList.innerHTML = "<p>Aucun fichier log trouvé</p>";
     return;
   }
    files.forEach(file => {
      const fileItem = document.createElement("div");
      fileItem.className = "file-item";
      fileItem.innerHTML = `
        <div class="file-info">
          <div class="file-details">
            <i class="bi bi-file-text"></i>
            <span class="file-name">${file.chemin}</span>
            <span class="file-type">${file.type_log}</span>
            <span class="file-date">${new Date(file.add_at).toLocaleDateString()}</span>
          </div>
          <div class="file-actions">
            <input type="radio" name="selectedLog" value="${file.id}" ${file.id === selectedLogId ? 'checked' : ''}>
            <button class="remove-file" onclick="deleteFile('${file.id}')">
              <i class="bi bi-x-circle"></i>
            </button>
          </div>
        </div>
      `;
      filesList.appendChild(fileItem);
    });

    // Gestion de la sélection
    document.querySelectorAll('input[name="selectedLog"]').forEach(radio => {
      radio.addEventListener('change', (e) => {
        selectedLogId = e.target.value;
        localStorage.setItem("currentLogId", selectedLogId);
      });
    });
  }

  // Fonction pour supprimer un fichier
  window.deleteFile = async function(logId) {
    if (!confirm("Êtes-vous sûr de vouloir supprimer ce fichier ?")) return;
    
    try {
      const res = await fetch(`http://localhost:5000/api/settings/logs/${logId}`, {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + token }
      });
      if (res.ok) {
        loadExistingFiles(); // Recharger la liste
        if (selectedLogId === logId) {
          selectedLogId = null;
          localStorage.removeItem("currentLogId");
        }
      }
    } catch (err) {
      console.error("Erreur lors de la suppression :", err);
    }
  };

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

  // Lancement de l'analyse
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
        clearSelectedFile();
        loadExistingFiles();
        // Stocke l'ID du fichier log pour le dashboard
        localStorage.setItem("currentLogId", data.id);
        console.log("ID stocké :", data.id);
        alert("Fichier enregistré avec succès !");
        console.log("Réponse de l'API :", data);
        window.location.href = "dashboard.html";
      } else {
        const error = await res.json();
        alert("Erreur lors de l'upload : " + error.msg);
      }
    } catch (err) {
      console.error("Erreur lors de l'envoi à l'API :", err);
      alert("Une erreur est survenue. Veuillez réessayer.");
    }
  });

});
