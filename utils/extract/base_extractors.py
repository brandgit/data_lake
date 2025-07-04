"""
Base extractor classes for JobTech utilities
Contains common functionality for API and scraping extractors
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

import requests
import pandas as pd

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration centralisée pour tous les extracteurs"""
    
    def __init__(self):
        # API Keys et tokens
        self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
        self.ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
        self.ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY')
        self.KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME')
        self.KAGGLE_KEY = os.getenv('KAGGLE_KEY')
        
        # Request settings
        self.REQUEST_TIMEOUT = 30
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        
        # Data directories (relative to project root)
        self.project_root = Path(__file__).parent.parent.parent
        self.raw_data_dir = self.project_root / 'raw'
        self.datasets_clean_dir = self.project_root / 'datasets_clean'
        
        # Create directories if they don't exist
        self.raw_data_dir.mkdir(exist_ok=True)
        self.datasets_clean_dir.mkdir(exist_ok=True)


class BaseAPIExtractor:
    """Classe de base pour tous les extracteurs utilisant des APIs"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JobTech-Extractor/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save_raw_data(self, df: pd.DataFrame, source: str, suffix: str = None):
        """
        Sauvegarde les données brutes avec timestamp et métadonnées
        
        Args:
            df: DataFrame à sauvegarder
            source: Nom de la source (ex: 'adzuna', 'github')
            suffix: Suffixe optionnel pour différencier les fichiers
        """
        if df.empty:
            self.logger.warning(f"DataFrame vide pour {source}, pas de sauvegarde")
            return None
            
        # Créer le sous-répertoire pour la source
        source_dir = self.config.raw_data_dir / source
        source_dir.mkdir(exist_ok=True)
        
        # Générer le nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_parts = [source, timestamp]
        if suffix:
            filename_parts.append(suffix)
        filename = f"{'_'.join(filename_parts)}.csv"
        filepath = source_dir / filename
        
        # Ajouter des métadonnées
        df_with_meta = df.copy()
        df_with_meta['extracted_at'] = datetime.now()
        df_with_meta['extractor_class'] = self.__class__.__name__
        
        # Sauvegarder
        df_with_meta.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"✅ Sauvegardé: {filepath} ({len(df)} lignes)")
        
        return filepath
    
    def delay_request(self, seconds: int = 2):
        """Délai entre les requêtes pour éviter le rate limiting"""
        time.sleep(seconds)
    
    def make_request(self, url: str, params: dict = None, max_retries: int = None) -> dict:
        """
        Effectue une requête HTTP avec retry automatique
        
        Args:
            url: URL à requêter
            params: Paramètres de la requête
            max_retries: Nombre max de tentatives (défaut: config)
            
        Returns:
            dict: Réponse JSON ou dict vide si échec
        """
        max_retries = max_retries or self.config.MAX_RETRIES
        retry_delay = self.config.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Requête {url} (tentative {attempt + 1}/{max_retries})")
                
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        f"Erreur tentative {attempt + 1}/{max_retries}: {e}. "
                        f"Retry dans {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponentiel
                else:
                    self.logger.error(f"Échec après {max_retries} tentatives: {e}")
                    return {}
        
        return {}
    
    def extract(self) -> pd.DataFrame:
        """Méthode principale d'extraction - à implémenter dans les sous-classes"""
        raise NotImplementedError("La méthode extract() doit être implémentée")


class BaseScrapeExtractor:
    """Classe de base pour tous les extracteurs utilisant du scraping/RSS"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save_raw_data(self, df: pd.DataFrame, source: str, suffix: str = None):
        """
        Sauvegarde les données brutes (même méthode que BaseAPIExtractor)
        """
        if df.empty:
            self.logger.warning(f"DataFrame vide pour {source}, pas de sauvegarde")
            return None
            
        # Créer le sous-répertoire pour la source
        source_dir = self.config.raw_data_dir / source
        source_dir.mkdir(exist_ok=True)
        
        # Générer le nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_parts = [source, timestamp]
        if suffix:
            filename_parts.append(suffix)
        filename = f"{'_'.join(filename_parts)}.csv"
        filepath = source_dir / filename
        
        # Ajouter des métadonnées
        df_with_meta = df.copy()
        df_with_meta['extracted_at'] = datetime.now()
        df_with_meta['extractor_class'] = self.__class__.__name__
        
        # Sauvegarder
        df_with_meta.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"✅ Sauvegardé: {filepath} ({len(df)} lignes)")
        
        return filepath
    
    def delay_request(self, seconds: int = 3):
        """Délai plus long pour le scraping pour éviter d'être détecté"""
        time.sleep(seconds)
    
    def make_request(self, url: str, headers: dict = None, max_retries: int = None) -> requests.Response:
        """
        Effectue une requête HTTP pour scraping avec retry automatique
        
        Args:
            url: URL à scraper
            headers: Headers supplémentaires
            max_retries: Nombre max de tentatives
            
        Returns:
            requests.Response: Objet Response ou None si échec
        """
        max_retries = max_retries or self.config.MAX_RETRIES
        retry_delay = self.config.RETRY_DELAY
        
        # Fusionner headers custom avec headers par défaut
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Scraping {url} (tentative {attempt + 1}/{max_retries})")
                
                response = self.session.get(
                    url,
                    headers=request_headers,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        f"Erreur tentative {attempt + 1}/{max_retries}: {e}. "
                        f"Retry dans {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponentiel
                else:
                    self.logger.error(f"Échec après {max_retries} tentatives: {e}")
                    return None
        
        return None
    
    def extract(self) -> pd.DataFrame:
        """Méthode principale d'extraction - à implémenter dans les sous-classes"""
        raise NotImplementedError("La méthode extract() doit être implémentée") 