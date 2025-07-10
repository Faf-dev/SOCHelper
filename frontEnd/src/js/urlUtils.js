class UrlUtils {
  static truncateUrl(url, maxLength = 45) {
    if (!url || url.length <= maxLength) {
      return url || '';
    }
    
    // Séparer le chemin et les paramètres
    if (url.includes('?')) {
      const [path, params] = url.split('?', 2);
      
      // Si le chemin seul est déjà trop long
      if (path.length >= maxLength - 3) {
        return path.substring(0, maxLength - 3) + '...';
      }
      
      // Calculer l'espace restant pour les paramètres
      const remaining = maxLength - path.length - 4;
      
      if (remaining > 0) {
        return `${path}?${params.substring(0, remaining)}...`;
      } else {
        return path + '?...';
      }
    } else {
      return url.substring(0, maxLength - 3) + '...';
    }
  }
  
  static createUrlCell(fullUrl) {
    const truncated = this.truncateUrl(fullUrl);
    const needsTooltip = fullUrl && fullUrl.length > 45;
    
    if (needsTooltip) {
      // Approche robuste avec event listeners
      return `
        <div class="url-cell" style="position: relative; cursor: pointer;" 
             data-full-url="${this.escapeHtml(fullUrl)}">
          <span class="url-text">${this.escapeHtml(truncated)}</span>
        </div>
      `;
    } else {
      return `
        <div class="url-cell">
          <span class="url-text">${this.escapeHtml(truncated)}</span>
        </div>
      `;
    }
  }
  
  static showTooltip(event, element) {
    const fullUrl = element.getAttribute('data-full-url');
    if (!fullUrl) return;
    
    // Supprimer tout tooltip existant
    this.hideTooltip();
    
    // Créer le tooltip
    const tooltip = document.createElement('div');
    tooltip.id = 'url-tooltip';
    tooltip.textContent = fullUrl; // textContent pour éviter les problèmes XSS
    tooltip.style.cssText = `
      position: fixed;
      background: #333;
      color: white;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 12px;
      max-width: 400px;
      word-wrap: break-word;
      z-index: 9999;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      pointer-events: none;
      white-space: pre-wrap;
      font-family: monospace;
    `;
    
    document.body.appendChild(tooltip);
    
    // Positionnement robuste
    const rect = tooltip.getBoundingClientRect();
    const mouseX = event.clientX || event.pageX || 0;
    const mouseY = event.clientY || event.pageY || 0;
    
    let x = mouseX + 10;
    let y = mouseY - rect.height - 10;
    
    // Ajustements pour rester dans la fenêtre
    if (x + rect.width > window.innerWidth) {
      x = window.innerWidth - rect.width - 10;
    }
    if (x < 10) x = 10;
    
    if (y < 10) {
      y = mouseY + 20;
    }
    
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }
    
  static hideTooltip() {
    const tooltip = document.getElementById('url-tooltip');
    if (tooltip) {
      tooltip.remove();
    }
  }
  
  static escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  // Initialiser les event listeners pour les tooltips
  static initTooltips() {
    // Utiliser la délégation d'événements pour gérer les éléments ajoutés dynamiquement
    document.addEventListener('mouseenter', (e) => {
      if (e.target.closest('.url-cell[data-full-url]')) {
        this.showTooltip(e, e.target.closest('.url-cell[data-full-url]'));
      }
    }, true);
    
    document.addEventListener('mouseleave', (e) => {
      if (e.target.closest('.url-cell[data-full-url]')) {
        this.hideTooltip();
      }
    }, true);
  }
}

// Rendre disponible globalement
window.UrlUtils = UrlUtils;

// Initialiser les tooltips au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
  UrlUtils.initTooltips();
});
