const { Notification } = require("electron");
const fs = require('fs');
const path = require('path');

class NotificationManager {
  constructor() {
    this.isEnabled = true;
  }

  // Notification pour injection SQL
  showSQLInjectionAlert(ip, date, heure) {
    if (!this.isEnabled) {
      console.log("Notifications désactivées");
      return;
    }
    
    console.log("Création de la notification pour:", { ip, date, heure });
    
    try {
      // Notification pour injection SQL
      const notification = new Notification({
        title: "ALERTE: Tentative injection SQL détectée",
        body: `${ip} - Le ${date} à ${heure}`,
      });
      
      notification.show();
      console.log("Notification affichée avec succès");
      
      // Événements optionnels pour debug
      notification.on('show', () => {
        console.log("Notification montrée");
      });
      
      notification.on('click', () => {
        console.log("Notification cliquée");
      });
      
    } catch (error) {
      console.error("Erreur lors de la création de la notification:", error);
    }
  }

  // Notification pour brute force
  showBruteForceAlert(ip, nombreTentatives, date, heure) {
    if (!this.isEnabled) return;
    
    const notification = new Notification({
      title: "ALERTE: Tentative brute force détecté",
      body: `${ip}: ${nombreTentatives} tentatives - Le ${date} à ${heure}`
    });
    
    notification.show();
  }

  // Activer/désactiver les notifications
  enable() {
    this.isEnabled = true;
  }

  disable() {
    this.isEnabled = false;
  }
}

module.exports = NotificationManager;
