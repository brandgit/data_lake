"""
Base cleaner classes and utilities for JobTech project
Contains common functionality for data cleaning
"""

import os
import pandas as pd
import numpy as np
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class CleaningStats:
    """Statistiques de nettoyage pour une source"""
    source: str
    files_processed: int
    rows_input: int
    rows_output: int
    rows_dropped: int
    issues_found: List[str]
    
    @property
    def drop_rate(self) -> float:
        if self.rows_input == 0:
            return 0.0
        return (self.rows_dropped / self.rows_input) * 100


class BaseDataCleaner:
    """Classe de base pour tous les nettoyeurs de données"""
    
    def __init__(self, raw_dir: str = "raw", clean_dir: str = "datasets_clean"):
        # Déterminer le chemin racine du projet
        self.project_root = Path(__file__).parent.parent.parent
        self.raw_dir = self.project_root / raw_dir
        self.clean_dir = self.project_root / clean_dir
        self.clean_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration des mappings et règles de nettoyage
        self._setup_mappings()
    
    def _setup_mappings(self):
        """Configure les mappings et règles de nettoyage"""
        
        # Dictionnaire de mapping des pays
        self.country_mapping = {
            'france': 'FR', 'francia': 'FR', 'frankreich': 'FR',
            'germany': 'DE', 'allemagne': 'DE', 'deutschland': 'DE',
            'netherlands': 'NL', 'pays-bas': 'NL', 'niederlande': 'NL',
            'belgium': 'BE', 'belgique': 'BE', 'belgien': 'BE',
            'spain': 'ES', 'espagne': 'ES', 'spanien': 'ES',
            'italy': 'IT', 'italie': 'IT', 'italien': 'IT',
            'united kingdom': 'GB', 'royaume-uni': 'GB', 'uk': 'GB',
            'poland': 'PL', 'pologne': 'PL', 'polen': 'PL',
            'sweden': 'SE', 'suède': 'SE', 'schweden': 'SE',
            'norway': 'NO', 'norvège': 'NO', 'norwegen': 'NO',
            'united states': 'US', 'usa': 'US', 'america': 'US',
            'worldwide': 'WW', 'remote': 'WW', 'global': 'WW'
        }
        
        # Technologies reconnues
        self.tech_keywords = {
            'languages': ['python', 'javascript', 'java', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'],
            'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'spring', 'laravel', 'express', 'next.js', 'nuxt'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'ansible', 'maven', 'gradle', 'webpack']
        }
        
        # Mapping pour harmonisation des technologies
        self.tech_mapping = {
            'Data scientist or machine learning specialist': 'data-science;machine-learning',
            'Developer, front-end': 'frontend',
            'Developer, back-end': 'backend', 
            'Developer, full-stack': 'fullstack',
            'Engineer, data': 'data-engineering',
            'Engineer, site reliability': 'sre;devops',
            'Developer, mobile': 'mobile',
            'Developer, desktop or enterprise applications': 'desktop;enterprise',
            'Developer, game or graphics': 'game-dev;graphics',
            'Developer, embedded applications or devices': 'embedded;iot',
            'DevOps specialist': 'devops',
            'Database administrator': 'database;sql',
            'System administrator': 'sysadmin',
            'Network engineer': 'networking',
            'Cloud infrastructure engineer': 'cloud;infrastructure',
            'Security engineer': 'security',
            'QA or test developer': 'testing;qa'
        }
        
        # Heuristiques pays pour Google Trends
        self.keyword_country_hints = {
            'python': 'US', 'javascript': 'US', 'java': 'US',
            'typescript': 'US', 'react': 'US', 'angular': 'US',
            'vue': 'FR', 'php': 'FR', 'symfony': 'FR',
            'laravel': 'GB', 'ruby': 'JP', 'go': 'US',
            'rust': 'US', 'swift': 'US', 'kotlin': 'US'
        }
    
    def normalize_country(self, country: str) -> str:
        """Normalise les noms de pays en codes ISO"""
        if pd.isna(country) or not country:
            return 'Unknown'
        
        country_clean = str(country).lower().strip()
        return self.country_mapping.get(country_clean, country_clean.upper()[:2])
    
    def clean_text_encoding(self, text: str) -> str:
        """Nettoie l'encodage UTF-8 et caractères problématiques"""
        if pd.isna(text) or text == "":
            return ""
        
        text = str(text)
        
        # Encoder/décoder en UTF-8 pour nettoyer l'encodage
        try:
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except:
            pass
        
        # Supprimer les caractères de contrôle problématiques
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Remplacer les caractères non-ASCII par des équivalents ASCII
        text = text.replace('é', 'e').replace('è', 'e').replace('à', 'a')
        text = text.replace('ù', 'u').replace('ô', 'o').replace('ç', 'c')
        text = text.replace('ñ', 'n').replace('ü', 'u').replace('ö', 'o')
        text = text.replace('ä', 'a').replace('ß', 'ss')
        
        # Nettoyer les guillemets doubles multiples
        text = re.sub(r'"+', '"', text)
        
        # Supprimer les retours à la ligne dans les descriptions
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_technologies(self, text: str) -> List[str]:
        """Extrait les technologies d'un texte"""
        if pd.isna(text) or not text:
            return []
        
        text_lower = str(text).lower()
        found_techs = []
        
        for category, techs in self.tech_keywords.items():
            for tech in techs:
                if tech in text_lower:
                    found_techs.append(tech)
        
        return list(set(found_techs))  # Supprimer les doublons
    
    def clean_salary(self, salary_val: Any) -> Optional[float]:
        """Nettoie et valide les valeurs de salaire"""
        if pd.isna(salary_val) or salary_val == '':
            return None
        
        try:
            salary = float(salary_val)
            # Filtrer les salaires aberrants (entre 10k et 500k EUR/USD)
            if 10000 <= salary <= 500000:
                return salary
            return None
        except (ValueError, TypeError):
            return None
    
    def harmonize_technologies(self, tech_string: str) -> str:
        """Harmonise le format des technologies vers format standard"""
        if pd.isna(tech_string) or tech_string == '':
            return ''
        
        tech_string = str(tech_string)
        
        # Si déjà au format standard (avec ;), nettoyer seulement
        if ';' in tech_string and ',' not in tech_string:
            techs = [t.strip().lower() for t in tech_string.split(';') if t.strip()]
            return ';'.join(sorted(set(techs)))
        
        # Traiter les formats legacy (avec virgules)
        if ',' in tech_string:
            techs = []
            parts = [p.strip() for p in tech_string.split(',')]
            
            for part in parts:
                if part in self.tech_mapping:
                    techs.extend(self.tech_mapping[part].split(';'))
                else:
                    # Extraire technologies du texte libre
                    extracted = self.extract_technologies(part)
                    techs.extend(extracted)
            
            # Nettoyer et déduplicater
            techs = [t.strip().lower() for t in techs if t.strip()]
            return ';'.join(sorted(set(techs)))
        
        # Texte libre - extraire les technologies
        extracted = self.extract_technologies(tech_string)
        if extracted:
            return ';'.join(sorted(set(extracted)))
        
        return tech_string.lower().strip()
    
    def harmonize_job_titles(self, title: str) -> str:
        """Harmonise les titres de poste vers format standard"""
        if pd.isna(title) or not title:
            return 'Other'
        
        title_lower = str(title).lower().strip()
        
        # Patterns de correspondance
        patterns = {
            'data-scientist': ['data scientist', 'machine learning', 'ml engineer', 'ai engineer'],
            'frontend-developer': ['front-end', 'frontend', 'front end', 'ui developer'],
            'backend-developer': ['back-end', 'backend', 'back end', 'server developer'],
            'fullstack-developer': ['full-stack', 'fullstack', 'full stack'],
            'devops-engineer': ['devops', 'site reliability', 'sre', 'infrastructure'],
            'mobile-developer': ['mobile', 'ios', 'android', 'react native', 'flutter'],
            'qa-engineer': ['qa', 'quality assurance', 'test engineer', 'testing'],
            'data-engineer': ['data engineer', 'data pipeline', 'etl'],
            'security-engineer': ['security', 'cybersecurity', 'infosec'],
            'product-manager': ['product manager', 'pm', 'product owner'],
            'software-engineer': ['software engineer', 'software developer', 'programmer']
        }
        
        for standard_title, keywords in patterns.items():
            if any(keyword in title_lower for keyword in keywords):
                return standard_title
        
        return 'other'
    
    def clean_html_content(self, html_content: str) -> str:
        """Nettoie le contenu HTML et extrait le texte"""
        if pd.isna(html_content) or not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(str(html_content), 'html.parser')
            # Extraire seulement le texte
            text = soup.get_text(separator=' ', strip=True)
            # Nettoyer l'encodage
            return self.clean_text_encoding(text)
        except Exception as e:
            self.logger.warning(f"Erreur nettoyage HTML: {e}")
            return self.clean_text_encoding(str(html_content))
    
    def get_files_for_source(self, source: str) -> List[Path]:
        """Récupère tous les fichiers pour une source donnée"""
        source_dir = self.raw_dir / source
        if not source_dir.exists():
            self.logger.warning(f"Répertoire source non trouvé: {source_dir}")
            return []
        
        # Chercher tous les fichiers CSV dans le répertoire
        files = list(source_dir.glob("*.csv"))
        self.logger.info(f"Trouvé {len(files)} fichiers pour {source}")
        return files
    
    def save_cleaned_data(self, df: pd.DataFrame, source: str, suffix: str = "clean") -> Path:
        """Sauvegarde les données nettoyées"""
        if df.empty:
            self.logger.warning(f"DataFrame vide pour {source}, pas de sauvegarde")
            return None
        
        # Nom de fichier avec suffix
        filename = f"{source}_{suffix}.csv"
        filepath = self.clean_dir / filename
        
        # Sauvegarder avec encodage UTF-8
        df.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"✅ Sauvegardé: {filepath} ({len(df)} lignes)")
        
        return filepath
    
    def clean_data(self, source: str) -> pd.DataFrame:
        """Méthode principale de nettoyage - à implémenter dans les sous-classes"""
        raise NotImplementedError("La méthode clean_data() doit être implémentée")


class DataCleaner(BaseDataCleaner):
    """Nettoyeur de données principal qui orchestre tous les nettoyeurs spécialisés"""
    
    def __init__(self, raw_dir: str = "raw", clean_dir: str = "datasets_clean"):
        super().__init__(raw_dir, clean_dir)
        self.stats: List[CleaningStats] = []
    
    def clean_all_sources(self) -> Dict[str, pd.DataFrame]:
        """Nettoie toutes les sources de données disponibles"""
        self.logger.info("🧹 Début du nettoyage de toutes les sources...")
        
        cleaned_data = {}
        sources = ['adzuna', 'github', 'kaggle', 'google_trends', 'stackoverflow', 'remoteok', 'indeed']
        
        for source in sources:
            try:
                self.logger.info(f"🔧 Nettoyage de {source}...")
                cleaned_df = self.clean_data(source)
                
                if not cleaned_df.empty:
                    cleaned_data[source] = cleaned_df
                    self.logger.info(f"✅ {source}: {len(cleaned_df)} lignes nettoyées")
                else:
                    self.logger.warning(f"❌ {source}: Aucune donnée après nettoyage")
                    
            except Exception as e:
                self.logger.error(f"Erreur lors du nettoyage de {source}: {e}")
                continue
        
        self.logger.info(f"🎯 Nettoyage terminé: {len(cleaned_data)} sources traitées")
        return cleaned_data
    
    def clean_data(self, source: str) -> pd.DataFrame:
        """Orchestre le nettoyage pour une source donnée"""
        # Cette méthode sera surchargée ou utilisera des nettoyeurs spécialisés
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
        # Charger tous les fichiers de la source
        all_data = []
        for file in files:
            try:
                df = pd.read_csv(file, encoding='utf-8')
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                self.logger.error(f"Erreur lecture {file}: {e}")
                continue
        
        if not all_data:
            return pd.DataFrame()
        
        # Concaténer tous les fichiers
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Nettoyage générique basique
        return self._apply_basic_cleaning(combined_df)
    
    def _apply_basic_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applique un nettoyage de base générique"""
        if df.empty:
            return df
        
        original_count = len(df)
        
        # Supprimer les doublons complets
        df = df.drop_duplicates()
        
        # Nettoyer l'encodage des colonnes texte
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].apply(self.clean_text_encoding)
        
        # Supprimer les lignes entièrement vides
        df = df.dropna(how='all')
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"Nettoyage de base: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df 