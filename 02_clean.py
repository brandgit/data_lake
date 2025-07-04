#!/usr/bin/env python3
"""
02_clean.py - Script de nettoyage des données JobTech
Utilise les classes utilitaires dans utils/clean/ pour nettoyer toutes les sources
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
        logging.FileHandler('clean.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal pour le nettoyage"""
    print("🧹 Démarrage du nettoyage des données JobTech...")
    logger.info("Début du processus de nettoyage JobTech")
    
    start_time = datetime.now()
    cleaning_results = {}
    
    try:
        # Importer toutes les classes de nettoyage depuis utils
        from utils.clean import (
            AdzunaDataCleaner, GitHubDataCleaner, KaggleDataCleaner,
            GoogleTrendsDataCleaner, StackOverflowDataCleaner,
            RemoteOKDataCleaner, IndeedDataCleaner, DataCleaner
        )
        
        print("\n🔧 === NETTOYAGE DES SOURCES INDIVIDUELLES ===")
        
        # 1. Nettoyage Adzuna (offres d'emploi)
        print("\n🔍 Nettoyage Adzuna...")
        try:
            adzuna_cleaner = AdzunaDataCleaner()
            adzuna_clean = adzuna_cleaner.clean_data("adzuna")
            if not adzuna_clean.empty:
                adzuna_cleaner.save_cleaned_data(adzuna_clean, "adzuna")
                cleaning_results['adzuna'] = len(adzuna_clean)
                print(f"✅ Adzuna: {len(adzuna_clean)} lignes nettoyées")
            else:
                cleaning_results['adzuna'] = 0
                print("❌ Adzuna: Aucune donnée après nettoyage")
        except Exception as e:
            logger.error(f"Erreur Adzuna: {e}")
            cleaning_results['adzuna'] = 0
        
        # 2. Nettoyage GitHub (repositories)
        print("\n🐙 Nettoyage GitHub...")
        try:
            github_cleaner = GitHubDataCleaner()
            github_clean = github_cleaner.clean_data("github")
            if not github_clean.empty:
                github_cleaner.save_cleaned_data(github_clean, "github")
                cleaning_results['github'] = len(github_clean)
                print(f"✅ GitHub: {len(github_clean)} lignes nettoyées")
            else:
                cleaning_results['github'] = 0
                print("❌ GitHub: Aucune donnée après nettoyage")
        except Exception as e:
            logger.error(f"Erreur GitHub: {e}")
            cleaning_results['github'] = 0
        
        # 3. Nettoyage Kaggle (données salariales)
        print("\n💰 Nettoyage Kaggle...")
        try:
            kaggle_cleaner = KaggleDataCleaner()
            kaggle_clean = kaggle_cleaner.clean_data("kaggle")
            if not kaggle_clean.empty:
                kaggle_cleaner.save_cleaned_data(kaggle_clean, "kaggle")
                cleaning_results['kaggle'] = len(kaggle_clean)
                print(f"✅ Kaggle: {len(kaggle_clean)} lignes nettoyées")
            else:
                cleaning_results['kaggle'] = 0
                print("❌ Kaggle: Aucune donnée après nettoyage")
        except Exception as e:
            logger.error(f"Erreur Kaggle: {e}")
            cleaning_results['kaggle'] = 0
        
        # 4. Nettoyage Google Trends
        print("\n📈 Nettoyage Google Trends...")
        try:
            trends_cleaner = GoogleTrendsDataCleaner()
            trends_clean = trends_cleaner.clean_data("google_trends")
            if not trends_clean.empty:
                trends_cleaner.save_cleaned_data(trends_clean, "google_trends")
                cleaning_results['google_trends'] = len(trends_clean)
                print(f"✅ Google Trends: {len(trends_clean)} lignes nettoyées")
            else:
                cleaning_results['google_trends'] = 0
                print("❌ Google Trends: Aucune donnée après nettoyage")
        except Exception as e:
            logger.error(f"Erreur Google Trends: {e}")
            cleaning_results['google_trends'] = 0
        
        # 5. Nettoyage StackOverflow
        print("\n📊 Nettoyage StackOverflow...")
        try:
            stackoverflow_cleaner = StackOverflowDataCleaner()
            stackoverflow_clean = stackoverflow_cleaner.clean_data("stackoverflow")
            if not stackoverflow_clean.empty:
                stackoverflow_cleaner.save_cleaned_data(stackoverflow_clean, "stackoverflow")
                cleaning_results['stackoverflow'] = len(stackoverflow_clean)
                print(f"✅ StackOverflow: {len(stackoverflow_clean)} lignes nettoyées")
            else:
                cleaning_results['stackoverflow'] = 0
                print("❌ StackOverflow: Aucune donnée après nettoyage")
        except Exception as e:
            logger.error(f"Erreur StackOverflow: {e}")
            cleaning_results['stackoverflow'] = 0
        
        # 6. Nettoyage RemoteOK
        print("\n🌐 Nettoyage RemoteOK...")
        try:
            remoteok_cleaner = RemoteOKDataCleaner()
            remoteok_clean = remoteok_cleaner.clean_data("remoteok")
            if not remoteok_clean.empty:
                remoteok_cleaner.save_cleaned_data(remoteok_clean, "remoteok")
                cleaning_results['remoteok'] = len(remoteok_clean)
                print(f"✅ RemoteOK: {len(remoteok_clean)} lignes nettoyées")
            else:
                cleaning_results['remoteok'] = 0
                print("❌ RemoteOK: Aucune donnée après nettoyage")
        except Exception as e:
            logger.error(f"Erreur RemoteOK: {e}")
            cleaning_results['remoteok'] = 0
        
        # 7. Nettoyage Indeed RSS
        print("\n📰 Nettoyage Indeed RSS...")
        try:
            indeed_cleaner = IndeedDataCleaner()
            indeed_clean = indeed_cleaner.clean_data("indeed")
            if not indeed_clean.empty:
                indeed_cleaner.save_cleaned_data(indeed_clean, "indeed")
                cleaning_results['indeed'] = len(indeed_clean)
                print(f"✅ Indeed: {len(indeed_clean)} lignes nettoyées")
            else:
                cleaning_results['indeed'] = 0
                print("❌ Indeed: Aucune donnée après nettoyage")
        except Exception as e:
            logger.error(f"Erreur Indeed: {e}")
            cleaning_results['indeed'] = 0
        
        # 8. Export SQL consolidé
        print("\n💾 === EXPORT SQL ===")
        try:
            export_to_sql(cleaning_results)
            print("✅ Export SQL généré")
        except Exception as e:
            logger.error(f"Erreur export SQL: {e}")
            print(f"❌ Erreur export SQL: {e}")
        
        # Résumé final
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*50)
        print("📋 RÉSUMÉ DU NETTOYAGE")
        print("="*50)
        
        total_cleaned = sum(cleaning_results.values())
        
        for source, count in cleaning_results.items():
            status = "✅" if count > 0 else "❌"
            print(f"{status} {source.capitalize()}: {count:,} lignes nettoyées")
        
        print(f"\n📊 Total: {total_cleaned:,} lignes nettoyées")
        print(f"⏱️ Durée: {duration}")
        print(f"📁 Données nettoyées dans: datasets_clean/")
        
        # Log final
        logger.info(f"Nettoyage terminé - {total_cleaned} lignes en {duration}")
        
        if total_cleaned > 0:
            print("\n✅ Nettoyage terminé avec succès!")
            return 0
        else:
            print("\n❌ Aucune donnée nettoyée!")
            return 1
        
    except Exception as e:
        logger.error(f"Erreur critique lors du nettoyage: {e}")
        print(f"\n💥 Erreur critique: {e}")
        return 1

def export_to_sql(cleaning_results):
    """Exporte les données nettoyées en format SQL dans datasets_clean/"""
    print("📄 Export des données nettoyées en format SQL...")
    
    datasets_clean_dir = Path("datasets_clean")
    sql_output_file = datasets_clean_dir / "jobtech_data.sql"
    
    try:
        with open(sql_output_file, 'w', encoding='utf-8') as sql_file:
            # En-tête SQL
            sql_file.write(f"""-- JobTech Data Export
-- Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Sources nettoyées: {', '.join(cleaning_results.keys())}
-- Total des lignes: {sum(cleaning_results.values()):,}

-- ==============================================
-- CRÉATION DE LA BASE DE DONNÉES JOBTECH
-- ==============================================

-- Supprimer la base si elle existe
DROP DATABASE IF EXISTS jobtech_dwh;
CREATE DATABASE jobtech_dwh;
USE jobtech_dwh;

-- ==============================================
-- TABLES PRINCIPALES
-- ==============================================

-- Table des offres d'emploi (Adzuna, RemoteOK, Indeed)
CREATE TABLE job_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(200),
    location VARCHAR(200),
    country VARCHAR(5),
    description TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    contract_type VARCHAR(100),
    technologies TEXT,
    job_title_standard VARCHAR(100),
    created_at DATETIME,
    cleaned_at DATETIME,
    INDEX idx_source (source),
    INDEX idx_country (country),
    INDEX idx_job_title (job_title_standard)
);

-- Table des repositories GitHub
CREATE TABLE github_repos (
    id BIGINT PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    language VARCHAR(50),
    stargazers_count INT DEFAULT 0,
    forks_count INT DEFAULT 0,
    technologies TEXT,
    popularity_category ENUM('low', 'medium', 'high', 'viral'),
    created_at DATETIME,
    updated_at DATETIME,
    cleaned_at DATETIME,
    INDEX idx_language (language),
    INDEX idx_popularity (popularity_category)
);

-- Table des données salariales (Kaggle, StackOverflow)
CREATE TABLE salary_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    job_title VARCHAR(200),
    job_title_standard VARCHAR(100),
    salary DECIMAL(10,2),
    experience_years INT,
    experience_level ENUM('junior', 'mid', 'senior', 'expert'),
    country VARCHAR(5),
    location VARCHAR(200),
    technologies TEXT,
    survey_year INT,
    cleaned_at DATETIME,
    INDEX idx_job_title (job_title_standard),
    INDEX idx_country (country),
    INDEX idx_experience (experience_level)
);

-- Table des tendances Google Trends
CREATE TABLE tech_trends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    interest INT CHECK (interest >= 0 AND interest <= 100),
    geo VARCHAR(10),
    tech_category VARCHAR(50),
    source VARCHAR(50),
    cleaned_at DATETIME,
    UNIQUE KEY unique_trend (keyword, date, geo),
    INDEX idx_keyword (keyword),
    INDEX idx_date (date),
    INDEX idx_geo (geo)
);

-- ==============================================
-- VUES ANALYTIQUES
-- ==============================================

-- Vue: Top technologies par offres d'emploi
CREATE VIEW v_top_technologies AS
SELECT 
    SUBSTRING_INDEX(SUBSTRING_INDEX(technologies, ';', numbers.n), ';', -1) as technology,
    COUNT(*) as job_count,
    COUNT(DISTINCT source) as source_count
FROM job_offers
CROSS JOIN (
    SELECT 1 n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
) numbers
WHERE technologies != ''
  AND CHAR_LENGTH(technologies) - CHAR_LENGTH(REPLACE(technologies, ';', '')) >= numbers.n - 1
GROUP BY technology
HAVING technology != ''
ORDER BY job_count DESC;

-- Vue: Salaires moyens par pays et expérience
CREATE VIEW v_salary_by_country_experience AS
SELECT 
    country,
    experience_level,
    COUNT(*) as sample_size,
    ROUND(AVG(salary), 2) as avg_salary,
    ROUND(MIN(salary), 2) as min_salary,
    ROUND(MAX(salary), 2) as max_salary
FROM salary_data 
WHERE salary IS NOT NULL 
GROUP BY country, experience_level
ORDER BY country, experience_level;

-- Vue: Tendances technologiques par pays
CREATE VIEW v_tech_trends_by_country AS
SELECT 
    keyword,
    geo as country,
    AVG(interest) as avg_interest,
    MIN(date) as first_date,
    MAX(date) as last_date,
    COUNT(*) as data_points
FROM tech_trends
GROUP BY keyword, geo
ORDER BY avg_interest DESC;

-- ==============================================
-- COMMENTAIRES ET MÉTADONNÉES
-- ==============================================

-- Ajouter des commentaires aux tables
ALTER TABLE job_offers COMMENT = 'Offres emploi agrégées (Adzuna, RemoteOK, Indeed)';
ALTER TABLE github_repos COMMENT = 'Repositories GitHub tendance par technologie';
ALTER TABLE salary_data COMMENT = 'Données salariales (Kaggle surveys, StackOverflow)';
ALTER TABLE tech_trends COMMENT = 'Tendances Google Trends pour technologies';

""")
            
            print(f"✅ Fichier SQL généré: {sql_output_file}")
            print(f"📊 Structure complète pour {len(cleaning_results)} sources")
            
    except Exception as e:
        logger.error(f"Erreur génération SQL: {e}")
        raise

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 