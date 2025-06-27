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
    
    return `
      <div class="url-cell" ${needsTooltip ? `data-full-url="${this.escapeHtml(fullUrl)}"` : ''}>
        <span class="url-text">${this.escapeHtml(truncated)}</span>
        ${needsTooltip ? `<div class="url-tooltip">${this.escapeHtml(fullUrl)}</div>` : ''}
      </div>
    `;
  }
  
  static escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Rendre disponible globalement
window.UrlUtils = UrlUtils;
