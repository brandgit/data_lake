#!/usr/bin/env python3
"""
03_load_dwh.py - Script de chargement vers le Data Warehouse JobTech
Utilise l'architecture modulaire avec utils/load/
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def main():
    """Point d'entrée principal pour le chargement DWH"""
    print("Démarrage du chargement vers le Data Warehouse JobTech...")
    print(f"Heure de début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Importer les classes utilitaires
        from utils.load import PostgreSQLDWHLoader, DatabaseConfig
        
        print("Initialisation du chargeur PostgreSQL DWH...")
        
        # Essayer de charger la configuration depuis config.py, sinon variables d'environnement
        project_root = Path(__file__).parent
        config_file = project_root / "config.py"
        
        if config_file.exists():
            config = DatabaseConfig.from_config_file(config_file)
            print("Configuration chargée depuis config.py")
        else:
            config = DatabaseConfig.from_env()
            print("Configuration chargée depuis les variables d'environnement")
        
        # Initialiser le chargeur principal
        loader = PostgreSQLDWHLoader(config)
        
        # Connexion à la base de données
        print("Connexion à PostgreSQL...")
        if not loader.connect():
            print("Impossible de se connecter à PostgreSQL")
            print("Vérifiez votre configuration de base de données")
            sys.exit(1)
        
        print("Création/mise à jour du schéma DWH...")
        if not loader.create_schema():
            print("Erreur lors de la création du schéma")
            sys.exit(1)
        
        print("Chargement des données vers le DWH...")
        success = loader.load_all_data()
        
        print("Génération du rapport de chargement...")
        loader.print_loading_summary()
        
        # Sauvegarder le rapport en JSON
        report = loader.generate_loading_report()
        report_file = project_root / f"load_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"Rapport sauvegardé: {report_file}")
        
        if success:
            print("Chargement DWH terminé avec succès!")
        else:
            print("Chargement DWH terminé avec des avertissements")
        
        print(f"Heure de fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Script 03_load_dwh.py terminé!")
        
    except ImportError as e:
        print(f"Module manquant: {e}")
        print("Assurez-vous que les modules utils/load/ sont correctement installés")
        sys.exit(1)
        
    except Exception as e:
        print(f"Erreur lors du chargement DWH: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 