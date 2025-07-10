function showAlert(message) {
    const alertBanner = document.getElementById('alert-banner');
    
    // Vérifier que les éléments existent
    if (!alertBanner) {
        console.error('Élément alert-banner introuvable dans le DOM');
        return;
    }
    
    if (message && message.trim() !== '') {
        alertBanner.innerHTML = message;
        alertBanner.style.display = 'flex';
    }
}

// Masque la bannière d'alerte
function hideAlert() {
    const alertBanner = document.getElementById('alert-banner');
    
    if (alertBanner) {
        alertBanner.style.display = 'none';
        alertBanner.innerHTML = '';
    }
}

// Récupère la dernière alerte créée depuis l'API
function getLastAlert() {
    fetch('http://localhost:5000/api/alert/latest')
        .then(response => response.json())
        .then(data => {
            if (data && data.ip) {
                const message = `<span class="icon"><i class="bi bi-exclamation-square"></i></span><strong>ALERTE:</strong> Tentative ${data.attackType} détectée depuis <strong>${data.ip}</strong> – Le ${data.date} à ${data.time}`;
                showAlert(message);
            } else {
                hideAlert();
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération de la dernière alerte:', error);
            hideAlert();
        });
}


function startAlertMonitoring() {
    // Vérifier immédiatement au chargement
    getLastAlert();
    
    // Puis vérifier toutes les 5 secondes
    setInterval(getLastAlert, 5000);
}

// Démarrer la surveillance quand la page est chargée
document.addEventListener('DOMContentLoaded', () => {
    startAlertMonitoring();
});
