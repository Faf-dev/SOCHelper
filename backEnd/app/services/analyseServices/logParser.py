import re
"""
Module pour parser les logs d'un fichier Apache ou Nginx
"""


def parseSingleLine(line):
    """Parse une seule ligne de log Apache/Nginx
    Retourne un dictionnaire ou None si la ligne n'est pas valide
    """
    pattern = r'"([^"]*)"'
    match = re.search(pattern, line)
    
    if not match:
        return None
    
    requestLine = match.group(1)
    requestParts = requestLine.split()
    
    if len(requestParts) < 2:
        return None
    
    method = requestParts[0]
    urlParts = requestParts[1:-1]  # Tout entre method et HTTP/1.
    url = ' '.join(urlParts)  # reconstitution de l'URL complète si espace

    parts = line.split()
    if len(parts) < 9:
        return None
        
    ip = parts[0]
    date = parts[3][1:12]  # Suppression de '['
    heure = parts[3][13:21]  # Suppression de ']'
    
    quoteParts = line.split('"')
    if len(quoteParts) >= 3:
        afterQuoteParts = quoteParts[2].split()
        statusCode = afterQuoteParts[0] if afterQuoteParts else "000"
    else:
       statusCode = "000"  # Code HTTP par défaut si non trouvé
    
    return {
        'ip': ip,
        'date': date,
        'heure': heure,
        'method': method,
        'url': url,
        'status_code': statusCode
    }
