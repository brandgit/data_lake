#!/usr/bin/env python3
"""
Script d'export du Data Warehouse JobTech vers un fichier SQL
Génère un export complet avec structure et données
"""

import os
import sys
import psycopg2
from datetime import datetime
import json

# Ajouter le répertoire parent au path pour importer config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config

def get_connection():
    """Établit une connexion à la base de données"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return None

def get_table_structure(cursor, table_name):
    """Récupère la structure d'une table"""
    cursor.execute(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        ORDER BY ordinal_position;
    """)
    return cursor.fetchall()

def get_table_data(cursor, table_name, limit=None):
    """Récupère les données d'une table"""
    limit_clause = f"LIMIT {limit}" if limit else ""
    cursor.execute(f"SELECT * FROM {table_name} {limit_clause};")
    return cursor.fetchall()

def escape_sql_value(value):
    """Échappe une valeur pour l'insertion SQL"""
    if value is None:
        return 'NULL'
    elif isinstance(value, str):
        # Échapper les apostrophes
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    else:
        escaped_str = str(value).replace("'", "''")
        return f"'{escaped_str}'"

def export_dwh_to_sql():
    """Export complet du DWH vers un fichier SQL"""
    
    conn = get_connection()
    if not conn:
        print("Impossible de se connecter à la base de données")
        return False
    
    cursor = conn.cursor()
    
    # Nom du fichier de sortie
    output_file = f"jobtech_dwh_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    print(f"Début de l'export du Data Warehouse vers {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # En-tête du fichier
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database_name = Config.DB_NAME
        
        f.write(f"""-- ============================================
-- Export Data Warehouse JobTech
-- Date: {current_time}
-- Base: {database_name}
-- ============================================

SET CLIENT_ENCODING TO 'UTF8';
SET STANDARD_CONFORMING_STRINGS TO ON;

""")
        
        # Tables à exporter dans l'ordre des dépendances
        tables = [
            # Tables de dimensions (pas de dépendances)
            'd_date',
            'd_country', 
            'd_company',
            'd_skill',
            'd_source',
            
            # Tables de faits (avec clés étrangères)
            'jobs',
            'github_repos',
            'google_trends',
            'developers',
            'kaggle_datasets'
        ]
        
        for table_name in tables:
            try:
                print(f"Export de la table: {table_name}")
                
                # Vérifier si la table existe
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    print(f"Table {table_name} non trouvée, passage à la suivante")
                    continue
                
                # Structure de la table
                f.write(f"\n-- ============================================\n")
                f.write(f"-- Table: {table_name.upper()}\n")
                f.write(f"-- ============================================\n\n")
                
                # Récupérer la définition complète de la table
                cursor.execute(f"""
                    SELECT 
                        column_name,
                        data_type,
                        character_maximum_length,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    ORDER BY ordinal_position;
                """)
                
                columns = cursor.fetchall()
                
                # CREATE TABLE
                f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n")
                f.write(f"CREATE TABLE {table_name} (\n")
                
                column_definitions = []
                for col in columns:
                    col_name, data_type, max_length, is_nullable, default = col
                    
                    # Type de données
                    if data_type == 'character varying' and max_length:
                        col_type = f"VARCHAR({max_length})"
                    elif data_type == 'character varying':
                        col_type = "TEXT"
                    elif data_type == 'integer':
                        col_type = "INTEGER"
                    elif data_type == 'bigint':
                        col_type = "BIGINT"
                    elif data_type == 'numeric':
                        col_type = "DECIMAL"
                    elif data_type == 'timestamp without time zone':
                        col_type = "TIMESTAMP"
                    elif data_type == 'date':
                        col_type = "DATE"
                    elif data_type == 'boolean':
                        col_type = "BOOLEAN"
                    else:
                        col_type = data_type.upper()
                    
                    # NULL/NOT NULL
                    nullable = "" if is_nullable == 'YES' else " NOT NULL"
                    
                    # DEFAULT
                    default_clause = f" DEFAULT {default}" if default else ""
                    
                    column_definitions.append(f"    {col_name} {col_type}{nullable}{default_clause}")
                
                f.write(",\n".join(column_definitions))
                f.write("\n);\n\n")
                
                # Données de la table
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                
                if row_count > 0:
                    print(f"    {row_count} lignes à exporter")
                    
                    # Limite pour éviter les fichiers trop volumineux
                    limit = 10000 if row_count > 10000 else None
                    if limit:
                        print(f"    Limitation à {limit} lignes pour éviter un fichier trop volumineux")
                    
                    # Récupérer les noms de colonnes
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}' 
                        ORDER BY ordinal_position;
                    """)
                    column_names = [row[0] for row in cursor.fetchall()]
                    
                    # Récupérer les données
                    data_rows = get_table_data(cursor, table_name, limit)
                    
                    if data_rows:
                        f.write(f"-- Données pour {table_name} ({len(data_rows)} lignes)\n")
                        
                        # Insérer par lots de 1000
                        batch_size = 1000
                        for i in range(0, len(data_rows), batch_size):
                            batch = data_rows[i:i + batch_size]
                            
                            f.write(f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES\n")
                            
                            values_list = []
                            for row in batch:
                                escaped_values = [escape_sql_value(val) for val in row]
                                values_list.append(f"({', '.join(escaped_values)})")
                            
                            f.write(",\n".join(values_list))
                            f.write(";\n\n")
                else:
                    f.write(f"-- Aucune donnée dans {table_name}\n\n")
                    
            except Exception as e:
                print(f"Erreur lors de l'export de {table_name}: {e}")
                f.write(f"-- ERREUR lors de l'export de {table_name}: {e}\n\n")
                continue
        
        # Vues
        f.write(f"\n-- ============================================\n")
        f.write(f"-- VUES\n")
        f.write(f"-- ============================================\n\n")
        
        # Vue jobs_consolidated
        f.write("""-- Vue consolidée des emplois
DROP VIEW IF EXISTS jobs_consolidated CASCADE;
CREATE VIEW jobs_consolidated AS
SELECT 
    j.*,
    dc.country_name,
    ds.source_name
FROM jobs j
LEFT JOIN d_country dc ON j.country = dc.iso2
LEFT JOIN d_source ds ON j.source = ds.source_name;

""")
        
        # Statistiques finales
        f.write(f"\n-- ============================================\n")
        f.write(f"-- STATISTIQUES DE L'EXPORT\n")
        f.write(f"-- ============================================\n\n")
        
        for table_name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                f.write(f"-- {table_name}: {count} lignes\n")
            except:
                f.write(f"-- {table_name}: table non accessible\n")
        
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"\n-- Export terminé le {end_time}\n")
    
    cursor.close()
    conn.close()
    
    # Statistiques du fichier
    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print("Export terminé avec succès !")
    print(f"Fichier: {output_file}")
    print(f"Taille: {file_size_mb:.2f} MB")
    
    return True

if __name__ == "__main__":
    export_dwh_to_sql() 