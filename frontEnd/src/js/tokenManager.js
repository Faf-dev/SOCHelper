class TokenManager {
  constructor() {
    this.lastActivity = Date.now();
    this.inactivityLimit = 30 * 60 * 1000; // 30 minutes d'inactivité max
    this.renewalInterval = 40 * 60 * 1000; // Vérification de l'inactivité toutes les 40 minutes
    this.renewalTimer = null;
    
    this.initActivityTracking();
    this.startTokenRenewal();
  }

  // Tracker l'activité utilisateur
  initActivityTracking() {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    events.forEach(event => {
      document.addEventListener(event, () => {
        this.lastActivity = Date.now();
      }, true);
    });
  }

  // Vérifier si l'utilisateur est actif
  isUserActive() {
    const now = Date.now();
    const timeSinceLastActivity = now - this.lastActivity;
    return timeSinceLastActivity < this.inactivityLimit;
  }

  // Renouveler le token seulement si actif
  async renewToken() {
    if (!this.isUserActive()) {
      console.log("Utilisateur inactif, pas de renouvellement du token");
      this.logout();
      return false;
    }

    try {
      const token = sessionStorage.getItem("token");
      if (!token) return false;

      const response = await fetch('http://localhost:5000/api/auth/refreshToken', {
        method: 'POST',
        headers: { "Authorization": "Bearer " + token }
      });

      if (response.ok) {
        const data = await response.json();
        sessionStorage.setItem('token', data.token);
        console.log("Token renouvelé avec succès");
        return true;
      } else {
        this.logout();
        return false;
      }
    } catch (error) {
      console.error("Erreur lors du renouvellement:", error);
      this.logout();
      return false;
    }
  }

  // Démarrer le système de renouvellement
  startTokenRenewal() {
    this.renewalTimer = setInterval(() => {
      this.renewToken();
    }, this.renewalInterval);
  }

  // Arrêter le renouvellement
  stopTokenRenewal() {
    if (this.renewalTimer) {
      clearInterval(this.renewalTimer);
      this.renewalTimer = null;
    }
  }

  // Déconnexion
  logout() {
    this.stopTokenRenewal();
    sessionStorage.clear();
    window.location.href = "login.html";
  }
}

// Initialisation du gestionnaire de token
const tokenManager = new TokenManager();
