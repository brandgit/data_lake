"""
API Extractors for JobTech utilities
Contains all API-based data extraction classes
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd

from .base_extractors import BaseAPIExtractor


class AdzunaExtractor(BaseAPIExtractor):
    """Extracteur de données depuis l'API Adzuna (offres d'emploi)"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.countries = ["fr", "de", "nl", "gb", "es", "it", "pl"]

    def extract(self, countries: List[str] = None) -> pd.DataFrame:
        """
        Extrait les offres d'emploi depuis Adzuna
        
        Args:
            countries: Liste des codes pays (défaut: tous les pays configurés)
            
        Returns:
            pd.DataFrame: Données d'offres d'emploi
        """
        if not self.config.ADZUNA_APP_ID or not self.config.ADZUNA_API_KEY:
            self.logger.warning("Adzuna API credentials non configurées")
            return pd.DataFrame()

        countries = countries or self.countries
        all_jobs = []

        for country in countries:
            self.logger.info(f"🔍 Extraction Adzuna pour {country.upper()}...")
            jobs = self._extract_jobs_for_country(country)
            if not jobs.empty:
                all_jobs.append(jobs)
            self.delay_request(2)

        if all_jobs:
            result = pd.concat(all_jobs, ignore_index=True)
            self.save_raw_data(result, "adzuna")
            self.logger.info(f"✅ Adzuna: {len(result)} offres extraites")
            return result

        return pd.DataFrame()

    def _extract_jobs_for_country(self, country: str) -> pd.DataFrame:
        """Extrait les offres pour un pays spécifique"""
        url = f"{self.base_url}/{country}/search/1"
        params = {
            "app_id": self.config.ADZUNA_APP_ID,
            "app_key": self.config.ADZUNA_API_KEY,
            "category": "it-jobs",
            "results_per_page": 50,
            "what": "developer OR programmer OR software engineer",
        }

        data = self.make_request(url, params)
        
        if not data or 'results' not in data:
            return pd.DataFrame()

        jobs = []
        for job in data.get('results', []):
            jobs.append({
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company", {}).get("display_name"),
                "location": job.get("location", {}).get("display_name"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "description": job.get("description"),
                "contract_type": job.get("contract_type"),
                "created": job.get("created"),
                "country": country.upper(),
                "source": "adzuna"
            })

        return pd.DataFrame(jobs)


class GitHubExtractor(BaseAPIExtractor):
    """Extracteur de repositories GitHub (projets tendance tech)"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.github.com"
        if self.config.GITHUB_TOKEN:
            self.session.headers["Authorization"] = f"token {self.config.GITHUB_TOKEN}"
        
        self.languages = ["python", "javascript", "java", "typescript", "go", "rust"]

    def extract(self, languages: List[str] = None, days: int = 7) -> pd.DataFrame:
        """
        Extrait les repositories GitHub tendance
        
        Args:
            languages: Liste des langages (défaut: langages configurés)
            days: Nombre de jours pour "récent" (défaut: 7)
            
        Returns:
            pd.DataFrame: Données des repositories
        """
        languages = languages or self.languages
        all_repos = []

        for language in languages:
            self.logger.info(f"🐙 Extraction GitHub pour {language}...")
            repos = self._extract_trending_repos(language, days)
            if not repos.empty:
                all_repos.append(repos)
            self.delay_request(1)  # Rate limiting GitHub

        if all_repos:
            result = pd.concat(all_repos, ignore_index=True)
            # Supprimer les doublons basés sur l'ID
            result = result.drop_duplicates(subset=['id'], keep='first')
            self.save_raw_data(result, "github")
            self.logger.info(f"✅ GitHub: {len(result)} repositories extraits")
            return result

        return pd.DataFrame()

    def _extract_trending_repos(self, language: str, days: int) -> pd.DataFrame:
        """Extrait les repos tendance pour un langage"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": f"language:{language} created:>{cutoff}",
            "sort": "stars",
            "order": "desc",
            "per_page": 100
        }

        data = self.make_request(url, params)
        
        if not data or 'items' not in data:
            return pd.DataFrame()

        repos = []
        for repo in data.get('items', []):
            repos.append({
                "id": repo.get("id"),
                "full_name": repo.get("full_name"),
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "html_url": repo.get("html_url"),
                "source": "github"
            })

        return pd.DataFrame(repos)


class RemoteOKExtractor(BaseAPIExtractor):
    """Extracteur d'offres d'emploi à distance depuis RemoteOK"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remoteok.io/api"

    def extract(self) -> pd.DataFrame:
        """
        Extrait les offres d'emploi à distance
        
        Returns:
            pd.DataFrame: Données des offres remote
        """
        self.logger.info("🌐 Extraction RemoteOK...")
        
        # RemoteOK ne nécessite pas d'auth mais a un format particulier
        url = self.base_url
        
        try:
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            # RemoteOK retourne une liste, le premier élément est souvent metadata
            if isinstance(data, list) and len(data) > 1:
                jobs_data = data[1:]  # Skip metadata
            else:
                self.logger.warning("Format de données RemoteOK inattendu")
                return pd.DataFrame()

            jobs = []
            for job in jobs_data:
                if isinstance(job, dict):
                    jobs.append({
                        "id": job.get("id"),
                        "position": job.get("position"),
                        "company": job.get("company"),
                        "location": job.get("location"),
                        "description": job.get("description"),
                        "tags": ",".join(job.get("tags", [])) if job.get("tags") else "",
                        "date": job.get("date"),
                        "url": job.get("url"),
                        "salary": job.get("salary"),
                        "source": "remoteok"
                    })

            result = pd.DataFrame(jobs)
            if not result.empty:
                self.save_raw_data(result, "remoteok")
                self.logger.info(f"✅ RemoteOK: {len(result)} offres extraites")
            
            return result

        except Exception as e:
            self.logger.error(f"Erreur RemoteOK: {e}")
            return pd.DataFrame()


class KaggleExtractor(BaseAPIExtractor):
    """Extracteur de datasets Kaggle (données salariales)"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.kaggle.com/api/v1"
        self._setup_kaggle_auth()

    def _setup_kaggle_auth(self):
        """Configure l'authentification Kaggle"""
        if self.config.KAGGLE_USERNAME and self.config.KAGGLE_KEY:
            import kaggle
            # Kaggle utilise les variables d'environnement
            import os
            os.environ['KAGGLE_USERNAME'] = self.config.KAGGLE_USERNAME
            os.environ['KAGGLE_KEY'] = self.config.KAGGLE_KEY

    def extract(self) -> pd.DataFrame:
        """
        Extrait et génère des données salariales basées sur des datasets Kaggle
        
        Returns:
            pd.DataFrame: Données salariales simulées
        """
        self.logger.info("💰 Génération de données salariales basées sur Kaggle...")
        
        # Plutôt que de télécharger des datasets volumineux,
        # on génère des données réalistes basées sur des études
        salary_data = self._generate_realistic_salary_data()
        
        if not salary_data.empty:
            self.save_raw_data(salary_data, "kaggle")
            self.logger.info(f"✅ Kaggle: {len(salary_data)} données salariales générées")
        
        return salary_data

    def _generate_realistic_salary_data(self, num_entries: int = 1000) -> pd.DataFrame:
        """Génère des données salariales réalistes"""
        
        job_titles = [
            "Software Engineer", "Data Scientist", "DevOps Engineer",
            "Frontend Developer", "Backend Developer", "Full Stack Developer",
            "Machine Learning Engineer", "Cloud Engineer", "Database Administrator",
            "Mobile Developer", "QA Engineer", "Product Manager"
        ]
        
        countries = ["FR", "DE", "GB", "NL", "ES", "IT", "US", "CA"]
        
        # Salaires de base par pays (en USD)
        base_salaries = {
            "US": 120000, "CA": 85000, "GB": 70000, "DE": 65000,
            "NL": 60000, "FR": 55000, "ES": 45000, "IT": 50000
        }
        
        # Multiplicateurs par type de poste
        role_multipliers = {
            "Software Engineer": 1.0, "Data Scientist": 1.2, "DevOps Engineer": 1.1,
            "Frontend Developer": 0.9, "Backend Developer": 1.0, "Full Stack Developer": 1.1,
            "Machine Learning Engineer": 1.3, "Cloud Engineer": 1.15, "Database Administrator": 0.95,
            "Mobile Developer": 1.05, "QA Engineer": 0.85, "Product Manager": 1.4
        }
        
        data = []
        for _ in range(num_entries):
            job_title = random.choice(job_titles)
            country = random.choice(countries)
            experience = random.randint(1, 15)
            
            # Calculer le salaire
            base = base_salaries[country]
            role_mult = role_multipliers[job_title]
            exp_mult = 1 + (experience - 1) * 0.08  # 8% par année d'expérience
            
            salary = int(base * role_mult * exp_mult * random.uniform(0.8, 1.2))
            
            data.append({
                "id": len(data),
                "job_title": job_title,
                "salary": salary,
                "experience_years": experience,
                "country": country,
                "location": f"City in {country}",
                "technologies": self._get_random_tech_stack(),
                "dataset_source": "kaggle-salary-survey-simulation",
                "source": "kaggle"
            })
        
        return pd.DataFrame(data)
    
    def _get_random_tech_stack(self) -> str:
        """Génère une stack technologique aléatoire"""
        all_techs = [
            "Python", "JavaScript", "Java", "TypeScript", "Go", "Rust", "C++",
            "React", "Vue.js", "Angular", "Django", "Flask", "Spring Boot",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "PostgreSQL", "MongoDB"
        ]
        
        num_techs = random.randint(3, 7)
        selected_techs = random.sample(all_techs, num_techs)
        return ";".join(selected_techs) 