#!/usr/bin/env python3
"""
01_scrape.py - Script d'extraction des données JobTech
Utilise les classes utilitaires dans utils/extract/ pour extraire depuis toutes les sources
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire utils au path
sys.path.append(str(Path(__file__).parent))

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('extract.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal pour l'extraction"""
    print("🚀 Démarrage de l'extraction des données JobTech...")
    logger.info("Début du processus d'extraction JobTech")
    
    start_time = datetime.now()
    extraction_results = {}
    
    try:
        # Importer toutes les classes d'extraction depuis utils
        from utils.extract import (
            AdzunaExtractor, GitHubExtractor, RemoteOKExtractor, KaggleExtractor,
            StackOverflowExtractor, GoogleTrendsExtractor, IndeedRSSExtractor
        )
        
        # 1. Extraction via APIs
        print("\n📡 === EXTRACTION VIA APIs ===")
        
        # Adzuna (offres d'emploi)
        print("\n🔍 Extraction Adzuna...")
        try:
            adzuna = AdzunaExtractor()
            adzuna_data = adzuna.extract(countries=["fr", "de", "nl"])
            extraction_results['adzuna'] = len(adzuna_data)
            print(f"✅ Adzuna: {len(adzuna_data)} offres extraites")
        except Exception as e:
            logger.error(f"Erreur Adzuna: {e}")
            extraction_results['adzuna'] = 0
        
        # GitHub (repositories tendance)
        print("\n🐙 Extraction GitHub...")
        try:
            github = GitHubExtractor()
            github_data = github.extract(languages=["python", "javascript", "java"])
            extraction_results['github'] = len(github_data)
            print(f"✅ GitHub: {len(github_data)} repositories extraits")
        except Exception as e:
            logger.error(f"Erreur GitHub: {e}")
            extraction_results['github'] = 0
        
        # RemoteOK (emplois à distance)
        print("\n🌐 Extraction RemoteOK...")
        try:
            remoteok = RemoteOKExtractor()
            remoteok_data = remoteok.extract()
            extraction_results['remoteok'] = len(remoteok_data)
            print(f"✅ RemoteOK: {len(remoteok_data)} offres extraites")
        except Exception as e:
            logger.error(f"Erreur RemoteOK: {e}")
            extraction_results['remoteok'] = 0
        
        # Kaggle (données salariales)
        print("\n💰 Génération données Kaggle...")
        try:
            kaggle = KaggleExtractor()
            kaggle_data = kaggle.extract()
            extraction_results['kaggle'] = len(kaggle_data)
            print(f"✅ Kaggle: {len(kaggle_data)} données salariales générées")
        except Exception as e:
            logger.error(f"Erreur Kaggle: {e}")
            extraction_results['kaggle'] = 0
        
        # 2. Extraction via Scraping/RSS
        print("\n🕷️ === EXTRACTION VIA SCRAPING/RSS ===")
        
        # StackOverflow Survey (données simulées)
        print("\n📊 Génération StackOverflow Survey...")
        try:
            stackoverflow = StackOverflowExtractor()
            stackoverflow_data = stackoverflow.extract(num_responses=500)
            extraction_results['stackoverflow'] = len(stackoverflow_data)
            print(f"✅ StackOverflow: {len(stackoverflow_data)} réponses générées")
        except Exception as e:
            logger.error(f"Erreur StackOverflow: {e}")
            extraction_results['stackoverflow'] = 0
        
        # Google Trends (tendances technologiques)
        print("\n📈 Extraction Google Trends...")
        try:
            trends = GoogleTrendsExtractor()
            trends_data = trends.extract()
            extraction_results['google_trends'] = len(trends_data)
            print(f"✅ Google Trends: {len(trends_data)} points de données extraits")
        except Exception as e:
            logger.error(f"Erreur Google Trends: {e}")
            extraction_results['google_trends'] = 0
        
        # Indeed RSS (flux RSS offres emploi)
        print("\n📰 Extraction Indeed RSS...")
        try:
            indeed = IndeedRSSExtractor()
            indeed_data = indeed.extract(countries=["fr", "de"])
            extraction_results['indeed'] = len(indeed_data)
            print(f"✅ Indeed RSS: {len(indeed_data)} offres extraites")
        except Exception as e:
            logger.error(f"Erreur Indeed RSS: {e}")
            extraction_results['indeed'] = 0
        
        # Résumé final
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*50)
        print("📋 RÉSUMÉ DE L'EXTRACTION")
        print("="*50)
        
        total_records = sum(extraction_results.values())
        
        for source, count in extraction_results.items():
            status = "✅" if count > 0 else "❌"
            print(f"{status} {source.capitalize()}: {count:,} enregistrements")
        
        print(f"\n📊 Total: {total_records:,} enregistrements extraits")
        print(f"⏱️ Durée: {duration}")
        print(f"📁 Données sauvegardées dans: raw/")
        
        # Log final
        logger.info(f"Extraction terminée - {total_records} enregistrements en {duration}")
        
        if total_records > 0:
            print("\n✅ Extraction terminée avec succès!")
            return 0
        else:
            print("\n❌ Aucune donnée extraite!")
            return 1
        
    except Exception as e:
        logger.error(f"Erreur critique lors de l'extraction: {e}")
        print(f"\n💥 Erreur critique: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 