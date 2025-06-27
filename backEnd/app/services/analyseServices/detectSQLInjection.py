from urllib.parse import unquote
"""
Module pour détecter les tentatives d'injection SQL dans une URL
Retourne True si une tentative est détectée, False sinon
"""


def detectSQLInjection(url):
    """
    Détecte les tentatives d'injection SQL dans une URL
    """
    if not url:
        return False
    
    # Création d'une liste de patterns suspects
    sqlPatterns = [
        'union', 'select', 'insert', 'update', 'delete', 'drop',
        'create', 'alter', 'exec', 'execute', 'sp_', 'xp_',
    
        # Opérateurs logiques
        'or 1=1', 'or 1=2', 'and 1=1', 'and 1=2', 'or true', 'or false',
        'or \'1\'=\'1\'', 'or "1"="1"', 'and \'1\'=\'1\'', 'and "1"="1"',
    
        # Commentaires SQL
        '--', '/*', '*/', '#',
    
        # Fonctions SQL communes
        'concat', 'substring', 'ascii', 'char', 'nchar', 'varchar',
        'cast', 'convert', 'database()', 'version()', 'user()',
        'system_user', 'session_user', 'current_user', 'current_database',
    
        # Échappements et encodages
        '%27', '%22', '%2d%2d', '%2f%2a', '%2a%2f',  # URL encodée: ', ", --, /*, */
        '0x', 'char(', 'ascii(',
    
        # Injections time-based
        'sleep(', 'waitfor delay', 'benchmark(', 'pg_sleep(',
    
        # Injections union-based
        'union all select', 'union select', 'union distinct',
        
        # Injections boolean-based
        'and (select', 'or (select', 'and exists', 'or exists',
        
        # Injections error-based
        'extractvalue(', 'updatexml(', 'exp(~(select',
        'floor(rand(0)*2)', 'group by x having',
        
        # Fonctions de hachage et crypto
        'md5(', 'sha1(', 'sha2(', 'password(',
        
        # Injections spécifiques aux SGBD
        # MySQL
        'information_schema', 'mysql.user', 'load_file(', 'into outfile',
        'into dumpfile', 'load data infile',
        
        # PostgreSQL
        'pg_user', 'pg_shadow', 'pg_database', 'pg_tables',
        'pg_stat_activity', 'pg_sleep(',
        
        # SQL Server
        'sysobjects', 'syscolumns', 'sysusers', 'master..xp_',
        'information_schema.tables', 'information_schema.columns',
        
        # Oracle
        'dual', 'all_tables', 'user_tables', 'all_tab_columns',
        'user_tab_columns', 'dbms_',
        
        # Techniques d'obfuscation
        'unhex(', 'hex(', 'bin(', 'oct(',
        
        # Patterns avec espaces/caractères spéciaux
        '/**/union', '/**/select', '/**/or', '/**/and',
        'uni/**/on', 'sel/**/ect',
        
        # Techniques de bypass WAF
        'union/**/select', 'and/**/1=1', 'or/**/1=1',
        'select/**/from', 'insert/**/into',
        
        # Encodage hexadécimal
        '0x3c2f7363726970743e',  # </script>
        '0x27', '0x22',  # ' et "
        
        # Techniques NoSQL (MongoDB, etc.)
        '$ne', '$gt', '$lt', '$where', '$regex', '$or', '$and',
        'javascript:', 'return true', 'return 1',
        
        # XPath injection (souvent combiné)
        'xpath', 'extractvalue', 'updatexml',
        
        # LDAP injection
        '*)(&', '*))%00', '*()|%26',
    ]
    
    decodedUrl = unquote(url).lower()  # Décodage de l'URL pour vérifier les encodages
    urlLower = url.lower()

    for testUrl in [decodedUrl, urlLower]:
        for pattern in sqlPatterns:
            if pattern in testUrl:
                return True
    
    return False
