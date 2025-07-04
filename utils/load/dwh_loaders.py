"""
Chargeurs spécialisés pour le Data Warehouse JobTech
"""

import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Optional
from datetime import datetime

from .base_loaders import BaseLoader, DatabaseConfig, LoadingStats

logger = logging.getLogger(__name__)


class PostgreSQLDWHLoader(BaseLoader):
    """Chargeur principal pour le Data Warehouse JobTech"""
    
    def __init__(self, config: DatabaseConfig = None):
        """Initialise le chargeur principal"""
        super().__init__(config)
        self.schema_created = False
        
        # Initialiser les chargeurs spécialisés
        self.jobs_loader = JobsLoader(config)
        self.github_loader = GitHubLoader(config)
        self.trends_loader = GoogleTrendsLoader(config)
        self.stackoverflow_loader = StackOverflowLoader(config)
        self.kaggle_loader = KaggleLoader(config)
        
        # Partager la connexion avec tous les sous-chargeurs
        self.sub_loaders = [
            self.jobs_loader,
            self.github_loader, 
            self.trends_loader,
            self.stackoverflow_loader,
            self.kaggle_loader
        ]
    
    def connect(self) -> bool:
        """Établit la connexion et la partage avec tous les sous-chargeurs"""
        if super().connect():
            # Partager la connexion avec tous les sous-chargeurs
            for loader in self.sub_loaders:
                loader.engine = self.engine
                loader.config = self.config
            return True
        return False
    
    def create_schema(self) -> bool:
        """Crée le schéma complet du Data Warehouse"""
        print("🔧 Création du schéma DWH...")
        
        schema_sql = """
        -- Schéma JobTech Data Warehouse
        
        -- Supprimer les tables existantes
        DROP TABLE IF EXISTS jobs CASCADE;
        DROP TABLE IF EXISTS github_repos CASCADE;
        DROP TABLE IF EXISTS google_trends CASCADE;
        DROP TABLE IF EXISTS developers CASCADE;
        DROP TABLE IF EXISTS kaggle_datasets CASCADE;
        DROP TABLE IF EXISTS d_date CASCADE;
        DROP TABLE IF EXISTS d_country CASCADE;
        DROP TABLE IF EXISTS d_company CASCADE;
        DROP TABLE IF EXISTS d_skill CASCADE;
        DROP TABLE IF EXISTS d_source CASCADE;
        
        -- Tables de dimensions
        CREATE TABLE d_date (
            date_key      DATE PRIMARY KEY,
            day           SMALLINT,
            month         SMALLINT,
            quarter       SMALLINT,
            year          SMALLINT,
            day_week      SMALLINT
        );

        CREATE TABLE d_country (
            id_country       SERIAL PRIMARY KEY,
            iso2             CHAR(2)  UNIQUE NOT NULL,
            country_name     TEXT,
            region           TEXT,
            monnaie_iso3     CHAR(3)
        );

        CREATE TABLE d_company (
            id_company        BIGSERIAL PRIMARY KEY,
            company_name      TEXT,
            workforce_size    TEXT,          -- ex: "0‑50", "51‑200"
            sector            TEXT
        );

        CREATE TABLE d_skill (
            id_skill          SERIAL PRIMARY KEY,
            skill_group       TEXT,          -- ex: "backend", "cloud"
            tech_label        TEXT           -- ex: "Python", "React"
        );
        
        CREATE TABLE d_source (
            id_source         SMALLSERIAL PRIMARY KEY,
            source_name       TEXT           -- "Indeed", "GitHub API" …
        );
        
        -- Table des offres d'emploi (Adzuna + RemoteOK)
        CREATE TABLE jobs (
            id VARCHAR(100) PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            company VARCHAR(300),
            location VARCHAR(300),
            country VARCHAR(10),
            salary_min NUMERIC(12,2),
            salary_max NUMERIC(12,2),
            salary_avg NUMERIC(12,2),
            salary VARCHAR(100),
            description TEXT,
            technologies TEXT,
            contract_type VARCHAR(100),
            source VARCHAR(50) NOT NULL,
            extracted_at TIMESTAMP,
            cleaned_at TIMESTAMP,
            loaded_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Table des repositories GitHub
        CREATE TABLE github_repos (
            repo_id BIGINT PRIMARY KEY,
            repo_name VARCHAR(500) NOT NULL,
            description TEXT,
            language VARCHAR(100),
            stars INTEGER DEFAULT 0,
            forks INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            source VARCHAR(50) DEFAULT 'github',
            cleaned_at TIMESTAMP,
            loaded_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Table des tendances Google Trends
        CREATE TABLE google_trends (
            id SERIAL PRIMARY KEY,
            keyword VARCHAR(200) NOT NULL,
            date DATE NOT NULL,
            interest_score INTEGER CHECK (interest_score >= 0 AND interest_score <= 100),
            country VARCHAR(10),
            source VARCHAR(50) DEFAULT 'google_trends',
            cleaned_at TIMESTAMP,
            loaded_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(keyword, date, country)
        );
        
        -- Table des développeurs StackOverflow
        CREATE TABLE developers (
            respondent_id INTEGER PRIMARY KEY,
            job_title VARCHAR(300),
            technologies TEXT,
            years_coding_pro VARCHAR(50),
            salary NUMERIC(12,2),
            employment VARCHAR(100),
            org_size VARCHAR(100),
            remote_work VARCHAR(50),
            country VARCHAR(100),
            source VARCHAR(50) DEFAULT 'stackoverflow',
            cleaned_at TIMESTAMP,
            loaded_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Table des datasets Kaggle
        CREATE TABLE kaggle_datasets (
            id INTEGER PRIMARY KEY,
            job_title VARCHAR(300),
            salary NUMERIC(12,2),
            experience_years INTEGER,
            location VARCHAR(300),
            technologies TEXT,
            dataset_source VARCHAR(500),
            source VARCHAR(50) DEFAULT 'kaggle',
            cleaned_at TIMESTAMP,
            loaded_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Index pour optimiser les requêtes
        CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
        CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country);
        CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
        CREATE INDEX IF NOT EXISTS idx_github_language ON github_repos(language);
        CREATE INDEX IF NOT EXISTS idx_github_stars ON github_repos(stars);
        CREATE INDEX IF NOT EXISTS idx_trends_keyword ON google_trends(keyword);
        CREATE INDEX IF NOT EXISTS idx_trends_date ON google_trends(date);
        CREATE INDEX IF NOT EXISTS idx_trends_country ON google_trends(country);
        CREATE INDEX IF NOT EXISTS idx_developers_title ON developers(job_title);
        CREATE INDEX IF NOT EXISTS idx_developers_country ON developers(country);
        CREATE INDEX IF NOT EXISTS idx_kaggle_title ON kaggle_datasets(job_title);
        
        -- Vue consolidée des emplois
        CREATE OR REPLACE VIEW v_jobs_consolidated AS
        SELECT 
            'job_' || ROW_NUMBER() OVER (ORDER BY source, id) as unified_id,
            id as source_id,
            title,
            company,
            location,
            country,
            COALESCE(salary_avg, (salary_min + salary_max) / 2) as estimated_salary,
            technologies,
            source,
            loaded_at
        FROM jobs
        WHERE title IS NOT NULL AND title != '';
        """
        
        success = self.execute_sql(schema_sql)
        if success:
            self.schema_created = True
            print("✅ Schéma DWH créé avec succès")
        else:
            print("❌ Erreur lors de la création du schéma")
        
        return success
    
    def populate_dimension_tables(self) -> bool:
        """Peuple les tables de dimensions avec des données de référence"""
        print("🏷️ Peuplement des tables de dimensions...")
        
        success = True
        
        # Peupler d_source avec les sources de données connues
        sources_sql = """
        INSERT INTO d_source (source_name) VALUES
        ('adzuna'),
        ('remoteok'),
        ('github'),
        ('google_trends'),
        ('stackoverflow'),
        ('kaggle')
        ON CONFLICT DO NOTHING;
        """
        
        # Peupler d_date avec une plage de dates (exemple: 2020-2030)
        date_sql = """
        INSERT INTO d_date (date_key, day, month, quarter, year, day_week)
        SELECT 
            d::date as date_key,
            EXTRACT(DAY FROM d)::SMALLINT as day,
            EXTRACT(MONTH FROM d)::SMALLINT as month,
            EXTRACT(QUARTER FROM d)::SMALLINT as quarter,
            EXTRACT(YEAR FROM d)::SMALLINT as year,
            EXTRACT(DOW FROM d)::SMALLINT as day_week
        FROM generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day'::interval) d
        ON CONFLICT DO NOTHING;
        """
        
        # Peupler d_country avec quelques pays de base
        countries_sql = """
        INSERT INTO d_country (iso2, country_name, region, monnaie_iso3) VALUES
        ('US', 'United States', 'North America', 'USD'),
        ('CA', 'Canada', 'North America', 'CAD'),
        ('GB', 'United Kingdom', 'Europe', 'GBP'),
        ('FR', 'France', 'Europe', 'EUR'),
        ('DE', 'Germany', 'Europe', 'EUR'),
        ('NL', 'Netherlands', 'Europe', 'EUR'),
        ('ES', 'Spain', 'Europe', 'EUR'),
        ('IT', 'Italy', 'Europe', 'EUR'),
        ('AU', 'Australia', 'Oceania', 'AUD'),
        ('IN', 'India', 'Asia', 'INR'),
        ('SG', 'Singapore', 'Asia', 'SGD'),
        ('BR', 'Brazil', 'South America', 'BRL'),
        ('MX', 'Mexico', 'North America', 'MXN'),
        ('JP', 'Japan', 'Asia', 'JPY'),
        ('KR', 'South Korea', 'Asia', 'KRW'),
        ('CN', 'China', 'Asia', 'CNY'),
        ('RU', 'Russia', 'Europe', 'RUB'),
        ('ZA', 'South Africa', 'Africa', 'ZAR'),
        ('NG', 'Nigeria', 'Africa', 'NGN'),
        ('EG', 'Egypt', 'Africa', 'EGP')
        ON CONFLICT (iso2) DO NOTHING;
        """
        
        # Exécuter les requêtes
        queries = [
            ("Sources", sources_sql),
            ("Dates", date_sql), 
            ("Pays", countries_sql)
        ]
        
        for name, sql in queries:
            try:
                if self.execute_sql(sql):
                    print(f"  ✅ {name} peuplés")
                else:
                    print(f"  ❌ Erreur lors du peuplement de {name}")
                    success = False
            except Exception as e:
                print(f"  ❌ Erreur {name}: {e}")
                success = False
        
        return success
    
    def load_all_data(self) -> bool:
        """Charge toutes les données dans le DWH"""
        print("📦 Chargement de toutes les données...")
        
        success = True
        
        # D'abord peupler les tables de dimensions
        success &= self.populate_dimension_tables()
        
        # Charger chaque type de données
        loaders_methods = [
            ("📋 Emplois", self.jobs_loader.load_all_jobs),
            ("🐙 GitHub", self.github_loader.load_github_data),
            ("📈 Google Trends", self.trends_loader.load_trends_data),
            ("💻 StackOverflow", self.stackoverflow_loader.load_stackoverflow_data),
            ("🔬 Kaggle", self.kaggle_loader.load_kaggle_data)
        ]
        
        for name, method in loaders_methods:
            print(f"\n{name}...")
            try:
                result = method()
                if not result:
                    print(f"⚠️ Avertissement: {name} - chargement partiel ou échoué")
                    success = False
            except Exception as e:
                print(f"❌ Erreur {name}: {e}")
                success = False
        
        # Collecter toutes les statistiques
        self.stats.extend(self.jobs_loader.stats)
        self.stats.extend(self.github_loader.stats)
        self.stats.extend(self.trends_loader.stats)
        self.stats.extend(self.stackoverflow_loader.stats)
        self.stats.extend(self.kaggle_loader.stats)
        
        # Peupler les dimensions dynamiques après le chargement des données
        if success:
            print("\n🔄 Peuplement des dimensions dynamiques...")
            success &= self.populate_dynamic_dimensions()
        
        return success
    
    def populate_dynamic_dimensions(self) -> bool:
        """Peuple les dimensions d_company et d_skill à partir des données réelles"""
        print("🔄 Peuplement des dimensions dynamiques...")
        
        success = True
        
        # Peupler d_company à partir des données jobs
        company_sql = """
        INSERT INTO d_company (company_name, workforce_size, sector)
        SELECT DISTINCT 
            company,
            NULL as workforce_size,
            NULL as sector
        FROM jobs 
        WHERE company IS NOT NULL AND company != ''
        ON CONFLICT DO NOTHING;
        """
        
        # Peupler d_skill à partir des technologies mentionnées
        # Cette requête extrait les technologies séparées par des virgules
        skill_sql = """
        WITH tech_split AS (
            SELECT DISTINCT 
                TRIM(unnest(string_to_array(technologies, ','))) as tech
            FROM jobs 
            WHERE technologies IS NOT NULL AND technologies != ''
            
            UNION
            
            SELECT DISTINCT 
                TRIM(unnest(string_to_array(technologies, ','))) as tech
            FROM developers 
            WHERE technologies IS NOT NULL AND technologies != ''
            
            UNION 
            
            SELECT DISTINCT 
                TRIM(unnest(string_to_array(technologies, ','))) as tech
            FROM kaggle_datasets 
            WHERE technologies IS NOT NULL AND technologies != ''
        )
        INSERT INTO d_skill (skill_group, tech_label)
        SELECT 
            CASE 
                WHEN LOWER(tech) LIKE ANY(ARRAY['%python%', '%java%', '%javascript%', '%c++%', '%c#%', '%php%', '%ruby%', '%go%', '%rust%', '%kotlin%', '%swift%']) 
                THEN 'programming_language'
                WHEN LOWER(tech) LIKE ANY(ARRAY['%react%', '%vue%', '%angular%', '%html%', '%css%', '%bootstrap%']) 
                THEN 'frontend'
                WHEN LOWER(tech) LIKE ANY(ARRAY['%django%', '%flask%', '%spring%', '%node%', '%express%', '%fastapi%']) 
                THEN 'backend'
                WHEN LOWER(tech) LIKE ANY(ARRAY['%aws%', '%azure%', '%gcp%', '%docker%', '%kubernetes%', '%cloud%']) 
                THEN 'cloud'
                WHEN LOWER(tech) LIKE ANY(ARRAY['%sql%', '%mysql%', '%postgresql%', '%mongodb%', '%redis%', '%database%']) 
                THEN 'database'
                WHEN LOWER(tech) LIKE ANY(ARRAY['%tensorflow%', '%pytorch%', '%ml%', '%ai%', '%data%', '%analytics%']) 
                THEN 'data_science'
                ELSE 'other'
            END as skill_group,
            tech as tech_label
        FROM tech_split 
        WHERE tech IS NOT NULL 
        AND LENGTH(tech) > 1 
        AND LENGTH(tech) < 50
        ON CONFLICT DO NOTHING;
        """
        
        # Exécuter les requêtes
        queries = [
            ("Entreprises", company_sql),
            ("Compétences", skill_sql)
        ]
        
        for name, sql in queries:
            try:
                if self.execute_sql(sql):
                    print(f"  ✅ {name} peuplées depuis les données")
                else:
                    print(f"  ❌ Erreur lors du peuplement de {name}")
                    success = False
            except Exception as e:
                print(f"  ❌ Erreur {name}: {e}")
                success = False
        
        return success


class JobsLoader(BaseLoader):
    """Chargeur pour les données d'emplois (Adzuna + RemoteOK)"""
    
    def load_all_jobs(self) -> bool:
        """Charge toutes les données d'emplois"""
        success = True
        
        success &= self.load_adzuna_data()
        success &= self.load_remoteok_data()
        
        return success
    
    def load_adzuna_data(self) -> bool:
        """Charge les données Adzuna"""
        csv_file = self.datasets_dir / "adzuna_clean.csv"
        if not csv_file.exists():
            logger.warning(f"Fichier {csv_file} non trouvé")
            return False
        
        try:
            df = pd.read_csv(csv_file)
            
            # Sélectionner et mapper seulement les colonnes nécessaires
            columns_mapping = {
                'id': 'id',
                'title': 'title', 
                'company': 'company',
                'location': 'location',
                'country': 'country',
                'salary_min': 'salary_min',
                'salary_max': 'salary_max',
                'description': 'description',
                'technologies': 'technologies',
                'contract_type': 'contract_type',
                'created': 'extracted_at',  # Mapper created vers extracted_at
                'cleaned_at': 'cleaned_at'
            }
            
            # Sélectionner seulement les colonnes qui existent
            available_cols = [col for col in columns_mapping.keys() if col in df.columns]
            df_mapped = df[available_cols].copy()
            df_mapped = df_mapped.rename(columns=columns_mapping)
            
            # Ajouter les colonnes requises
            df_mapped['source'] = 'adzuna'
            df_mapped['loaded_at'] = datetime.now()
            
            # Calculer salary_avg si on a min et max
            if 'salary_min' in df_mapped.columns and 'salary_max' in df_mapped.columns:
                df_mapped['salary_avg'] = (
                    pd.to_numeric(df_mapped['salary_min'], errors='coerce') + 
                    pd.to_numeric(df_mapped['salary_max'], errors='coerce')
                ) / 2
                df_mapped['salary_avg'] = df_mapped['salary_avg'].fillna(0)
            
            stats = self.load_dataframe(df_mapped, 'jobs', if_exists='append')
            print(f"  ✅ Adzuna: {stats.inserted_rows} emplois chargés")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement Adzuna: {e}")
            return False
    
    def load_remoteok_data(self) -> bool:
        """Charge les données RemoteOK"""
        csv_file = self.datasets_dir / "remoteok_clean.csv"
        if not csv_file.exists():
            logger.warning(f"Fichier {csv_file} non trouvé")
            return False
        
        try:
            df = pd.read_csv(csv_file)
            
            # Mapping des colonnes RemoteOK vers le schéma jobs
            columns_mapping = {
                'id': 'id',
                'position': 'title',  # RemoteOK utilise 'position'
                'company': 'company',
                'location': 'location',
                'description': 'description',
                'tags': 'technologies',  # RemoteOK utilise 'tags'
                'cleaned_at': 'cleaned_at'
            }
            
            # Sélectionner seulement les colonnes qui existent
            available_cols = [col for col in columns_mapping.keys() if col in df.columns]
            df_mapped = df[available_cols].copy()
            df_mapped = df_mapped.rename(columns=columns_mapping)
            
            # Ajouter les colonnes requises
            df_mapped['source'] = 'remoteok'
            df_mapped['loaded_at'] = datetime.now()
            
            # Ajouter des valeurs par défaut pour les colonnes manquantes
            if 'country' not in df_mapped.columns:
                df_mapped['country'] = 'REMOTE'  # RemoteOK = emplois distants
            if 'salary_min' not in df_mapped.columns:
                df_mapped['salary_min'] = None
            if 'salary_max' not in df_mapped.columns:
                df_mapped['salary_max'] = None
            if 'salary_avg' not in df_mapped.columns:
                df_mapped['salary_avg'] = None
            if 'contract_type' not in df_mapped.columns:
                df_mapped['contract_type'] = 'remote'
            if 'extracted_at' not in df_mapped.columns:
                df_mapped['extracted_at'] = None
            
            # Nettoyer les champs numériques (remplacer chaînes vides par NULL)
            for col in ['salary_min', 'salary_max', 'salary_avg']:
                if col in df_mapped.columns:
                    df_mapped[col] = df_mapped[col].replace('', None)
                    df_mapped[col] = pd.to_numeric(df_mapped[col], errors='coerce')
            
            stats = self.load_dataframe(df_mapped, 'jobs', if_exists='append')
            print(f"  ✅ RemoteOK: {stats.inserted_rows} emplois chargés")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement RemoteOK: {e}")
            return False


class GitHubLoader(BaseLoader):
    """Chargeur pour les données GitHub"""
    
    def load_github_data(self) -> bool:
        """Charge les données GitHub"""
        csv_file = self.datasets_dir / "github_clean.csv"
        if not csv_file.exists():
            logger.warning(f"Fichier {csv_file} non trouvé")
            return False
        
        try:
            df = pd.read_csv(csv_file)
            
            # Mapping des colonnes GitHub vers le schéma github_repos
            columns_mapping = {
                'id': 'repo_id',
                'full_name': 'repo_name',
                'description': 'description',
                'language': 'language',
                'stargazers_count': 'stars',
                'forks_count': 'forks',
                'created_at': 'created_at',
                'cleaned_at': 'cleaned_at'
            }
            
            # Sélectionner seulement les colonnes qui existent
            available_cols = [col for col in columns_mapping.keys() if col in df.columns]
            df_mapped = df[available_cols].copy()
            df_mapped = df_mapped.rename(columns=columns_mapping)
            
            # Ajouter les colonnes requises
            df_mapped['source'] = 'github'
            df_mapped['loaded_at'] = datetime.now()
            
            # Convertir les dates
            if 'created_at' in df_mapped.columns:
                df_mapped['created_at'] = pd.to_datetime(df_mapped['created_at'], errors='coerce')
            
            # Convertir les compteurs en entiers
            for col in ['stars', 'forks']:
                if col in df_mapped.columns:
                    df_mapped[col] = pd.to_numeric(df_mapped[col], errors='coerce').fillna(0).astype(int)
            
            stats = self.load_dataframe(df_mapped, 'github_repos', if_exists='append')
            print(f"  ✅ GitHub: {stats.inserted_rows} repositories chargés")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement GitHub: {e}")
            return False


class GoogleTrendsLoader(BaseLoader):
    """Chargeur pour les données Google Trends"""
    
    def load_trends_data(self) -> bool:
        """Charge les données Google Trends"""
        csv_file = self.datasets_dir / "google_trends_clean.csv"
        if not csv_file.exists():
            logger.warning(f"Fichier {csv_file} non trouvé")
            return False
        
        try:
            df = pd.read_csv(csv_file)
            
            # Mapping des colonnes Google Trends vers le schéma google_trends
            columns_mapping = {
                'keyword': 'keyword',
                'date': 'date',
                'interest': 'interest_score',  # Google Trends utilise 'interest'
                'geo': 'country',  # Google Trends utilise 'geo'
                'cleaned_at': 'cleaned_at'
            }
            
            # Sélectionner seulement les colonnes qui existent
            available_cols = [col for col in columns_mapping.keys() if col in df.columns]
            df_mapped = df[available_cols].copy()
            df_mapped = df_mapped.rename(columns=columns_mapping)
            
            # Ajouter les colonnes requises
            df_mapped['source'] = 'google_trends'
            df_mapped['loaded_at'] = datetime.now()
            
            # Convertir les dates
            if 'date' in df_mapped.columns:
                df_mapped['date'] = pd.to_datetime(df_mapped['date'], errors='coerce').dt.date
            
            # Convertir interest_score en entier
            if 'interest_score' in df_mapped.columns:
                df_mapped['interest_score'] = pd.to_numeric(df_mapped['interest_score'], errors='coerce').fillna(0).astype(int)
            
            # Supprimer les doublons potentiels
            if all(col in df_mapped.columns for col in ['keyword', 'date', 'country']):
                df_mapped = df_mapped.drop_duplicates(subset=['keyword', 'date', 'country'])
            
            stats = self.load_dataframe(df_mapped, 'google_trends', if_exists='append')
            print(f"  ✅ Google Trends: {stats.inserted_rows} tendances chargées")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement Google Trends: {e}")
            return False


class StackOverflowLoader(BaseLoader):
    """Chargeur pour les données StackOverflow"""
    
    def load_stackoverflow_data(self) -> bool:
        """Charge les données StackOverflow"""
        csv_file = self.datasets_dir / "stackoverflow_clean.csv"
        if not csv_file.exists():
            logger.warning(f"Fichier {csv_file} non trouvé")
            return False
        
        try:
            df = pd.read_csv(csv_file)
            
            # Mapping des colonnes StackOverflow vers le schéma developers
            columns_mapping = {
                'ResponseId': 'respondent_id',
                'DevType': 'job_title',
                'LanguageHaveWorkedWith': 'technologies',
                'YearsCodePro': 'years_coding_pro',
                'ConvertedCompYearly': 'salary',
                'Employment': 'employment',
                'OrgSize': 'org_size',
                'RemoteWork': 'remote_work',
                'Country': 'country',
                'cleaned_at': 'cleaned_at'
            }
            
            # Sélectionner seulement les colonnes qui existent
            available_cols = [col for col in columns_mapping.keys() if col in df.columns]
            df_mapped = df[available_cols].copy()
            df_mapped = df_mapped.rename(columns=columns_mapping)
            
            # Ajouter les colonnes requises
            df_mapped['source'] = 'stackoverflow'
            df_mapped['loaded_at'] = datetime.now()
            
            # Convertir les types de données
            if 'salary' in df_mapped.columns:
                df_mapped['salary'] = pd.to_numeric(df_mapped['salary'], errors='coerce')
            
            if 'years_coding_pro' in df_mapped.columns:
                # Convertir years_coding_pro en string (car le schéma utilise VARCHAR)
                df_mapped['years_coding_pro'] = df_mapped['years_coding_pro'].astype(str)
            
            stats = self.load_dataframe(df_mapped, 'developers', if_exists='append')
            print(f"  ✅ StackOverflow: {stats.inserted_rows} développeurs chargés")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement StackOverflow: {e}")
            return False


class KaggleLoader(BaseLoader):
    """Chargeur pour les données Kaggle"""
    
    def load_kaggle_data(self) -> bool:
        """Charge les données Kaggle"""
        csv_file = self.datasets_dir / "kaggle_clean.csv"
        if not csv_file.exists():
            logger.warning(f"Fichier {csv_file} non trouvé")
            return False
        
        try:
            df = pd.read_csv(csv_file)
            
            # Mapping des colonnes Kaggle vers le schéma kaggle_datasets
            columns_mapping = {
                'id': 'id',
                'job_title': 'job_title',
                'salary': 'salary',
                'experience_years': 'experience_years',
                'location': 'location',
                'technologies': 'technologies',
                'dataset_source': 'dataset_source',
                'cleaned_at': 'cleaned_at'
            }
            
            # Sélectionner seulement les colonnes qui existent
            available_cols = [col for col in columns_mapping.keys() if col in df.columns]
            df_mapped = df[available_cols].copy()
            df_mapped = df_mapped.rename(columns=columns_mapping)
            
            # Ajouter les colonnes requises
            df_mapped['source'] = 'kaggle'
            df_mapped['loaded_at'] = datetime.now()
            
            # Convertir les types de données
            if 'salary' in df_mapped.columns:
                df_mapped['salary'] = pd.to_numeric(df_mapped['salary'], errors='coerce')
            
            if 'experience_years' in df_mapped.columns:
                df_mapped['experience_years'] = pd.to_numeric(df_mapped['experience_years'], errors='coerce').fillna(0).astype(int)
            
            stats = self.load_dataframe(df_mapped, 'kaggle_datasets', if_exists='append')
            print(f"  ✅ Kaggle: {stats.inserted_rows} datasets chargés")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement Kaggle: {e}")
            return False 