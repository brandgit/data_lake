"""
Specialized data cleaners for JobTech project
Contains cleaning classes for each data source
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .base_cleaners import BaseDataCleaner, CleaningStats


class AdzunaDataCleaner(BaseDataCleaner):
    """Nettoyeur spécialisé pour les données Adzuna (offres d'emploi)"""
    
    def clean_data(self, source: str = "adzuna") -> pd.DataFrame:
        """Nettoie les données Adzuna"""
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
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
        
        df = pd.concat(all_data, ignore_index=True)
        return self._clean_adzuna_dataframe(df)
    
    def _clean_adzuna_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame Adzuna"""
        original_count = len(df)
        issues = []
        
        # Colonnes attendues
        expected_columns = ['title', 'company', 'location', 'salary_min', 'salary_max', 
                          'description', 'contract_type', 'created', 'country', 'source']
        
        # Vérifier les colonnes manquantes
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            issues.append(f"Colonnes manquantes: {missing_cols}")
            for col in missing_cols:
                df[col] = None
        
        # Supprimer les doublons basés sur titre + entreprise + localisation
        df = df.drop_duplicates(subset=['title', 'company', 'location'], keep='first')
        
        # Nettoyer les colonnes texte
        text_columns = ['title', 'company', 'location', 'description', 'contract_type']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.clean_text_encoding)
        
        # Nettoyer les descriptions HTML
        if 'description' in df.columns:
            df['description'] = df['description'].apply(self.clean_html_content)
        
        # Normaliser les pays
        if 'country' in df.columns:
            df['country'] = df['country'].apply(self.normalize_country)
        
        # Nettoyer les salaires
        for sal_col in ['salary_min', 'salary_max']:
            if sal_col in df.columns:
                df[sal_col] = df[sal_col].apply(self.clean_salary)
        
        # Harmoniser les titres de poste
        if 'title' in df.columns:
            df['job_title_standard'] = df['title'].apply(self.harmonize_job_titles)
        
        # Extraire les technologies de la description
        if 'description' in df.columns:
            df['technologies'] = df['description'].apply(
                lambda x: ';'.join(self.extract_technologies(x)) if x else ''
            )
        
        # Supprimer les lignes sans titre ni entreprise
        df = df.dropna(subset=['title', 'company'], how='all')
        
        # Ajouter timestamp de nettoyage
        df['cleaned_at'] = datetime.now()
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"Adzuna: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df


class GitHubDataCleaner(BaseDataCleaner):
    """Nettoyeur spécialisé pour les données GitHub (repositories)"""
    
    def clean_data(self, source: str = "github") -> pd.DataFrame:
        """Nettoie les données GitHub"""
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
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
        
        df = pd.concat(all_data, ignore_index=True)
        return self._clean_github_dataframe(df)
    
    def _clean_github_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame GitHub"""
        original_count = len(df)
        
        # Supprimer les doublons basés sur l'ID
        if 'id' in df.columns:
            df = df.drop_duplicates(subset=['id'], keep='first')
        
        # Nettoyer les colonnes texte
        text_columns = ['full_name', 'name', 'description', 'language']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.clean_text_encoding)
        
        # Valider les compteurs (étoiles, forks)
        for count_col in ['stargazers_count', 'forks_count']:
            if count_col in df.columns:
                df[count_col] = pd.to_numeric(df[count_col], errors='coerce').fillna(0).astype(int)
        
        # Normaliser les langages
        if 'language' in df.columns:
            df['language'] = df['language'].str.lower().replace('', 'unknown')
        
        # Extraire les technologies du nom et description
        tech_text = df[['name', 'description']].fillna('').apply(
            lambda row: f"{row['name']} {row['description']}", axis=1
        )
        df['technologies'] = tech_text.apply(
            lambda x: ';'.join(self.extract_technologies(x)) if x else ''
        )
        
        # Catégoriser par popularité
        if 'stargazers_count' in df.columns:
            df['popularity_category'] = pd.cut(
                df['stargazers_count'],
                bins=[0, 10, 100, 1000, float('inf')],
                labels=['low', 'medium', 'high', 'viral']
            )
        
        # Supprimer les repos sans nom
        df = df.dropna(subset=['name'])
        
        # Ajouter timestamp de nettoyage
        df['cleaned_at'] = datetime.now()
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"GitHub: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df


class KaggleDataCleaner(BaseDataCleaner):
    """Nettoyeur spécialisé pour les données Kaggle (salaires)"""
    
    def clean_data(self, source: str = "kaggle") -> pd.DataFrame:
        """Nettoie les données Kaggle"""
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
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
        
        df = pd.concat(all_data, ignore_index=True)
        return self._clean_kaggle_dataframe(df)
    
    def _clean_kaggle_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame Kaggle"""
        original_count = len(df)
        
        # Supprimer les doublons
        df = df.drop_duplicates()
        
        # Nettoyer les colonnes texte
        text_columns = ['job_title', 'country', 'location', 'technologies']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.clean_text_encoding)
        
        # Normaliser les pays
        if 'country' in df.columns:
            df['country'] = df['country'].apply(self.normalize_country)
        
        # Valider les salaires
        if 'salary' in df.columns:
            df['salary_clean'] = df['salary'].apply(self.clean_salary)
            # Garder seulement les salaires valides
            df = df.dropna(subset=['salary_clean'])
        
        # Harmoniser les titres de poste
        if 'job_title' in df.columns:
            df['job_title_standard'] = df['job_title'].apply(self.harmonize_job_titles)
        
        # Harmoniser les technologies
        if 'technologies' in df.columns:
            df['technologies_clean'] = df['technologies'].apply(self.harmonize_technologies)
        
        # Valider l'expérience
        if 'experience_years' in df.columns:
            df['experience_years'] = pd.to_numeric(df['experience_years'], errors='coerce')
            df = df[(df['experience_years'] >= 0) & (df['experience_years'] <= 50)]
        
        # Catégoriser les niveaux d'expérience
        if 'experience_years' in df.columns:
            df['experience_level'] = pd.cut(
                df['experience_years'],
                bins=[0, 2, 5, 10, float('inf')],
                labels=['junior', 'mid', 'senior', 'expert']
            )
        
        # Ajouter timestamp de nettoyage
        df['cleaned_at'] = datetime.now()
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"Kaggle: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df


class GoogleTrendsDataCleaner(BaseDataCleaner):
    """Nettoyeur spécialisé pour les données Google Trends"""
    
    def clean_data(self, source: str = "google_trends") -> pd.DataFrame:
        """Nettoie les données Google Trends"""
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
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
        
        df = pd.concat(all_data, ignore_index=True)
        return self._clean_google_trends_dataframe(df)
    
    def _clean_google_trends_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame Google Trends"""
        original_count = len(df)
        
        # Supprimer les doublons basés sur keyword + date + geo
        df = df.drop_duplicates(subset=['keyword', 'date', 'geo'], keep='first')
        
        # Nettoyer le nom des mots-clés
        if 'keyword' in df.columns:
            df['keyword'] = df['keyword'].apply(self.clean_text_encoding).str.lower()
        
        # Valider les valeurs d'intérêt (0-100)
        if 'interest' in df.columns:
            df['interest'] = pd.to_numeric(df['interest'], errors='coerce')
            df = df[(df['interest'] >= 0) & (df['interest'] <= 100)]
        
        # Normaliser les géolocalisations
        if 'geo' in df.columns:
            df['geo'] = df['geo'].apply(self.normalize_country)
        
        # Convertir les dates
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
        
        # Remplir les pays manquants avec heuristiques
        df = self._fill_missing_countries_google_trends(df)
        
        # Ajouter catégorie de technologie
        if 'keyword' in df.columns:
            df['tech_category'] = df['keyword'].apply(self._categorize_technology)
        
        # Ajouter timestamp de nettoyage
        df['cleaned_at'] = datetime.now()
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"Google Trends: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df
    
    def _fill_missing_countries_google_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remplit les pays manquants avec des heuristiques"""
        def guess_country(row):
            if pd.notna(row.get('geo')) and row['geo'] != '':
                return row['geo']
            
            keyword = str(row.get('keyword', '')).lower()
            return self.keyword_country_hints.get(keyword, 'Global')
        
        if 'geo' in df.columns:
            df['geo'] = df.apply(guess_country, axis=1)
        
        return df
    
    def _categorize_technology(self, keyword: str) -> str:
        """Catégorise une technologie par type"""
        if pd.isna(keyword):
            return 'other'
        
        keyword_lower = str(keyword).lower()
        
        for category, techs in self.tech_keywords.items():
            if keyword_lower in techs:
                return category
        
        return 'other'


class StackOverflowDataCleaner(BaseDataCleaner):
    """Nettoyeur spécialisé pour les données StackOverflow Survey"""
    
    def clean_data(self, source: str = "stackoverflow") -> pd.DataFrame:
        """Nettoie les données StackOverflow"""
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
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
        
        df = pd.concat(all_data, ignore_index=True)
        return self._clean_stackoverflow_dataframe(df)
    
    def _clean_stackoverflow_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame StackOverflow"""
        original_count = len(df)
        
        # Supprimer les doublons basés sur ResponseId si disponible
        if 'ResponseId' in df.columns:
            df = df.drop_duplicates(subset=['ResponseId'], keep='first')
        
        # Normaliser les pays
        if 'Country' in df.columns:
            df['Country'] = df['Country'].apply(self.normalize_country)
        
        # Nettoyer les salaires
        salary_columns = ['ConvertedCompYearly', 'CompTotal', 'salary']
        for col in salary_columns:
            if col in df.columns:
                df[f'{col}_clean'] = df[col].apply(self.clean_salary)
        
        # Harmoniser les types de développeurs
        if 'DevType' in df.columns:
            df['DevType_standard'] = df['DevType'].apply(self.harmonize_job_titles)
        
        # Harmoniser les technologies
        lang_columns = ['LanguageHaveWorkedWith', 'LanguageWantToWorkWith', 'technologies']
        for col in lang_columns:
            if col in df.columns:
                df[f'{col}_clean'] = df[col].apply(self.harmonize_technologies)
        
        # Valider l'âge
        if 'Age' in df.columns:
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
            df = df[(df['Age'] >= 16) & (df['Age'] <= 80)]
        
        # Valider les années d'expérience
        exp_columns = ['YearsCodePro', 'YearsCode', 'experience_years']
        for col in exp_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df[(df[col] >= 0) & (df[col] <= 50)]
        
        # Ajouter timestamp de nettoyage
        df['cleaned_at'] = datetime.now()
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"StackOverflow: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df


class RemoteOKDataCleaner(BaseDataCleaner):
    """Nettoyeur spécialisé pour les données RemoteOK"""
    
    def clean_data(self, source: str = "remoteok") -> pd.DataFrame:
        """Nettoie les données RemoteOK"""
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
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
        
        df = pd.concat(all_data, ignore_index=True)
        return self._clean_remoteok_dataframe(df)
    
    def _clean_remoteok_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame RemoteOK"""
        original_count = len(df)
        
        # Supprimer les doublons basés sur ID ou position + company
        if 'id' in df.columns:
            df = df.drop_duplicates(subset=['id'], keep='first')
        else:
            df = df.drop_duplicates(subset=['position', 'company'], keep='first')
        
        # Nettoyer les colonnes texte
        text_columns = ['position', 'company', 'location', 'description', 'tags']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.clean_text_encoding)
        
        # Harmoniser les titres de poste
        if 'position' in df.columns:
            df['job_title_standard'] = df['position'].apply(self.harmonize_job_titles)
        
        # Extraire les technologies des tags et description
        tech_sources = []
        if 'tags' in df.columns:
            tech_sources.append(df['tags'])
        if 'description' in df.columns:
            tech_sources.append(df['description'])
        
        if tech_sources:
            combined_text = pd.concat(tech_sources, axis=1).fillna('').apply(
                lambda row: ' '.join(row.values), axis=1
            )
            df['technologies'] = combined_text.apply(
                lambda x: ';'.join(self.extract_technologies(x)) if x else ''
            )
        
        # Nettoyer les salaires si présents
        if 'salary' in df.columns:
            df['salary_clean'] = df['salary'].apply(self.clean_salary)
        
        # Toutes les offres RemoteOK sont remote
        df['work_type'] = 'remote'
        df['country'] = 'WW'  # Worldwide
        
        # Ajouter timestamp de nettoyage
        df['cleaned_at'] = datetime.now()
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"RemoteOK: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df


class IndeedDataCleaner(BaseDataCleaner):
    """Nettoyeur spécialisé pour les données Indeed RSS"""
    
    def clean_data(self, source: str = "indeed") -> pd.DataFrame:
        """Nettoie les données Indeed"""
        files = self.get_files_for_source(source)
        if not files:
            return pd.DataFrame()
        
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
        
        df = pd.concat(all_data, ignore_index=True)
        return self._clean_indeed_dataframe(df)
    
    def _clean_indeed_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame Indeed"""
        original_count = len(df)
        
        # Supprimer les doublons basés sur titre + entreprise
        df = df.drop_duplicates(subset=['title', 'company'], keep='first')
        
        # Nettoyer les colonnes texte
        text_columns = ['title', 'company', 'location', 'description', 'salary']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.clean_text_encoding)
        
        # Nettoyer les descriptions HTML
        if 'description' in df.columns:
            df['description'] = df['description'].apply(self.clean_html_content)
        
        # Normaliser les pays
        if 'country' in df.columns:
            df['country'] = df['country'].apply(self.normalize_country)
        
        # Harmoniser les titres de poste
        if 'title' in df.columns:
            df['job_title_standard'] = df['title'].apply(self.harmonize_job_titles)
        
        # Extraire les technologies de la description
        if 'description' in df.columns:
            df['technologies'] = df['description'].apply(
                lambda x: ';'.join(self.extract_technologies(x)) if x else ''
            )
        
        # Nettoyer les salaires si format texte
        if 'salary' in df.columns:
            df['salary_clean'] = df['salary'].apply(self._extract_salary_from_text)
        
        # Convertir les dates de publication
        if 'published' in df.columns:
            df['published'] = pd.to_datetime(df['published'], errors='coerce')
        
        # Supprimer les lignes sans titre
        df = df.dropna(subset=['title'])
        
        # Ajouter timestamp de nettoyage
        df['cleaned_at'] = datetime.now()
        
        final_count = len(df)
        dropped = original_count - final_count
        
        self.logger.info(f"Indeed: {original_count} → {final_count} lignes ({dropped} supprimées)")
        
        return df
    
    def _extract_salary_from_text(self, salary_text: str) -> Optional[float]:
        """Extrait un salaire numérique depuis un texte"""
        if pd.isna(salary_text) or not salary_text:
            return None
        
        import re
        
        # Patterns pour extraire les salaires
        patterns = [
            r'(\d+)\s*k€',  # 50k€
            r'(\d+)\s*000\s*€',  # 50000€
            r'€\s*(\d+)',  # €50000
            r'(\d+)\s*€',  # 50€ (probablement horaire)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(salary_text).replace(',', ''))
            if match:
                value = float(match.group(1))
                # Convertir k€ en valeur complète
                if 'k€' in salary_text:
                    value *= 1000
                # Filtrer les valeurs raisonnables
                if 10000 <= value <= 500000:
                    return value
        
        return None 