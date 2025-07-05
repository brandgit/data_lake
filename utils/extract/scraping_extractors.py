"""
Scraping Extractors for JobTech utilities
Contains all scraping and RSS-based data extraction classes
"""

import random
import re
import time
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import feedparser
from bs4 import BeautifulSoup

from .base_extractors import BaseScrapeExtractor


class StackOverflowExtractor(BaseScrapeExtractor):
    """Extracteur de données Stack Overflow Developer Survey (simulé avec données réalistes)"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://insights.stackoverflow.com/survey/"

    def extract(self, num_responses: int = 1000, year: int = 2023) -> pd.DataFrame:
        """
        Génère des données simulées de l'enquête Stack Overflow
        
        Args:
            num_responses: Nombre de réponses à générer
            year: Année de l'enquête
            
        Returns:
            pd.DataFrame: Données d'enquête simulées
        """
        self.logger.info(f"Génération de {num_responses} réponses Stack Overflow Survey {year}...")
        
        survey_data = self._generate_developer_survey_data(num_responses, year)
        
        if not survey_data.empty:
            self.save_raw_data(survey_data, "stackoverflow")
            self.logger.info(f"StackOverflow: {len(survey_data)} réponses générées")
        
        return survey_data

    def _generate_developer_survey_data(self, num_responses: int, year: int) -> pd.DataFrame:
        """Génère des données d'enquête développeurs réalistes"""
        
        countries = [
            "France", "Germany", "Netherlands", "Belgium", "Spain", "Italy",
            "United Kingdom", "Poland", "Sweden", "Norway", "United States", "Canada"
        ]
        
        dev_types = [
            "Full-stack developer", "Back-end developer", "Front-end developer",
            "Mobile developer", "DevOps specialist", "Data scientist",
            "Desktop developer", "Database administrator", "System administrator",
            "Machine learning engineer", "Cloud engineer", "Security engineer"
        ]
        
        languages = [
            "JavaScript;Python;HTML/CSS;SQL",
            "Python;SQL;JavaScript;Bash/Shell",
            "Java;JavaScript;HTML/CSS;SQL", 
            "C#;JavaScript;HTML/CSS;SQL",
            "Python;JavaScript;TypeScript;SQL",
            "Go;Python;JavaScript;Docker",
            "React;Node.js;JavaScript;MongoDB",
            "Python;Django;PostgreSQL;Redis",
            "TypeScript;React;Node.js;GraphQL",
            "Java;Spring Boot;PostgreSQL;Kubernetes"
        ]
        
        # Salaires moyens par pays (en USD)
        salary_ranges = {
            "France": (35000, 80000), "Germany": (45000, 95000),
            "Netherlands": (40000, 85000), "Belgium": (38000, 75000),
            "Spain": (25000, 60000), "Italy": (28000, 65000),
            "United Kingdom": (40000, 100000), "Poland": (20000, 50000),
            "Sweden": (42000, 90000), "Norway": (50000, 110000),
            "United States": (60000, 180000), "Canada": (45000, 120000)
        }
        
        employment_types = [
            "Employed full-time", "Employed part-time", "Freelancer",
            "Independent contractor", "Self-employed"
        ]
        
        org_sizes = [
            "2-9 employees", "10-19 employees", "20-99 employees",
            "100-499 employees", "500-999 employees", "1000+ employees"
        ]
        
        remote_options = ["Never", "Rarely", "Sometimes", "Often", "Always"]
        
        data = []
        for i in range(num_responses):
            years_exp = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20])
            country = random.choice(countries)
            sal_min, sal_max = salary_ranges[country]
            
            # Ajuster le salaire selon l'expérience
            base_salary = random.randint(sal_min, sal_max)
            if years_exp < 2:
                salary = int(base_salary * 0.7)
            elif years_exp > 10:
                salary = int(base_salary * 1.4)
            else:
                salary = int(base_salary * (0.8 + years_exp * 0.05))
            
            data.append({
                "ResponseId": 50000 + i,
                "Country": country,
                "YearsCodePro": years_exp,
                "DevType": random.choice(dev_types),
                "LanguageHaveWorkedWith": random.choice(languages),
                "ConvertedCompYearly": salary,
                "Employment": random.choice(employment_types),
                "OrgSize": random.choice(org_sizes),
                "RemoteWork": random.choice(remote_options),
                "EdLevel": random.choice([
                    "Bachelor's degree", "Master's degree", "Some college",
                    "High school", "PhD", "Bootcamp"
                ]),
                "Age": random.randint(18, 65),
                "Gender": random.choice(["Man", "Woman", "Non-binary", "Prefer not to say"]),
                "source": "stackoverflow_survey",
                "survey_year": year
            })
        
        return pd.DataFrame(data)


class GoogleTrendsExtractor(BaseScrapeExtractor):
    """Extracteur de données Google Trends pour les technologies"""

    def __init__(self):
        super().__init__()
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl="en-US", tz=360)
            self.pytrends_available = True
        except Exception as e:
            self.logger.warning(f"PyTrends non disponible: {e}")
            self.pytrends = None
            self.pytrends_available = False
        
        # Groupes de mots-clés technologiques
        self.tech_keywords = [
            # Langages principaux
            ["Python", "JavaScript", "Java", "TypeScript", "C++"],
            ["Go", "Rust", "Ruby", "PHP", "Swift"],
            # Frameworks front-end
            ["React", "Vue.js", "Angular", "Svelte", "Next.js"],
            # Frameworks back-end
            ["Django", "Flask", "Spring Boot", "Laravel", "Express.js"],
            # Cloud & DevOps
            ["Docker", "Kubernetes", "AWS", "Azure", "GCP"],
            # Bases de données
            ["PostgreSQL", "MongoDB", "Redis", "MySQL", "Elasticsearch"]
        ]

    def extract(self, keyword_groups: List[List[str]] = None, 
                timeframe: str = "today 12-m", regions: List[str] = None) -> pd.DataFrame:
        """
        Extrait les tendances Google pour les technologies
        
        Args:
            keyword_groups: Groupes de mots-clés (max 5 par groupe)
            timeframe: Période d'analyse (défaut: 12 derniers mois)
            regions: Liste des régions (défaut: quelques pays)
            
        Returns:
            pd.DataFrame: Données de tendances
        """
        keyword_groups = keyword_groups or self.tech_keywords
        regions = regions or ["", "US", "FR", "DE", "GB"]  # Mondial + quelques pays
        
        all_trends = []
        
        if not self.pytrends_available:
            # Générer des données simulées si PyTrends n'est pas disponible
            self.logger.info("Génération de données Google Trends simulées...")
            return self._generate_simulated_trends_data(keyword_groups, regions)
        
        for region in regions:
            self.logger.info(f"Extraction Google Trends pour région: {region or 'Global'}")
            
            for group in keyword_groups:
                try:
                    trends = self._extract_trends_for_group(group, timeframe, region)
                    if not trends.empty:
                        all_trends.append(trends)
                    
                    # Délai important pour éviter le rate limiting
                    self.delay_request(5)
                    
                except Exception as e:
                    self.logger.warning(f"Erreur Google Trends pour {group}: {e}")
                    continue
        
        if all_trends:
            result = pd.concat(all_trends, ignore_index=True)
            self.save_raw_data(result, "google_trends")
            self.logger.info(f"Google Trends: {len(result)} points de données extraits")
            return result
        
        return pd.DataFrame()

    def _extract_trends_for_group(self, keywords: List[str], timeframe: str, geo: str) -> pd.DataFrame:
        """Extrait les tendances pour un groupe de mots-clés"""
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
            trends_data = self.pytrends.interest_over_time()
            
            if trends_data.empty:
                return pd.DataFrame()
            
            # Reformater les données
            result = []
            for date_index, row in trends_data.iterrows():
                for keyword in keywords:
                    if keyword in row:
                        result.append({
                            "keyword": keyword,
                            "date": date_index.date(),
                            "interest": row[keyword],
                            "geo": geo or "Global",
                            "source": "google_trends"
                        })
            
            return pd.DataFrame(result)
            
        except Exception as e:
            self.logger.error(f"Erreur extraction groupe {keywords}: {e}")
            return pd.DataFrame()

    def _generate_simulated_trends_data(self, keyword_groups: List[List[str]], 
                                      regions: List[str]) -> pd.DataFrame:
        """Génère des données de tendances simulées"""
        data = []
        
        # Générer des données pour les 12 derniers mois
        start_date = datetime.now() - timedelta(days=365)
        
        for keyword_group in keyword_groups:
            for keyword in keyword_group:
                for region in regions:
                    # Générer une tendance réaliste pour chaque mot-clé
                    base_interest = random.randint(20, 90)
                    
                    for week in range(52):  # 52 semaines
                        date = start_date + timedelta(weeks=week)
                        
                        # Ajouter de la variation naturelle
                        variation = random.uniform(0.7, 1.3)
                        seasonal_factor = 1 + 0.2 * random.sin(week * 2 * 3.14159 / 52)
                        
                        interest = min(100, max(0, int(base_interest * variation * seasonal_factor)))
                        
                        data.append({
                            "keyword": keyword,
                            "date": date.date(),
                            "interest": interest,
                            "geo": region or "Global",
                            "source": "google_trends_simulated"
                        })
        
        return pd.DataFrame(data)


class IndeedRSSExtractor(BaseScrapeExtractor):
    """Extracteur d'offres d'emploi depuis les flux RSS Indeed"""

    def __init__(self):
        super().__init__()
        self.base_urls = {
            "fr": "https://fr.indeed.com/rss",
            "de": "https://de.indeed.com/rss", 
            "uk": "https://uk.indeed.com/rss",
            "nl": "https://nl.indeed.com/rss",
            "es": "https://es.indeed.com/rss",
            "it": "https://it.indeed.com/rss"
        }

    def extract(self, countries: List[str] = None, 
                search_terms: List[str] = None) -> pd.DataFrame:
        """
        Extrait les offres d'emploi depuis les flux RSS Indeed
        
        Args:
            countries: Liste des codes pays
            search_terms: Termes de recherche
            
        Returns:
            pd.DataFrame: Données des offres d'emploi
        """
        countries = countries or ["fr", "de", "uk"]
        search_terms = search_terms or ["développeur", "developer", "programmer"]
        
        all_jobs = []
        
        for country in countries:
            self.logger.info(f"Extraction Indeed RSS pour {country.upper()}...")
            
            for term in search_terms:
                jobs = self._extract_jobs_rss(country, term)
                if not jobs.empty:
                    all_jobs.append(jobs)
                
                self.delay_request(3)  # Délai entre requêtes RSS
        
        if all_jobs:
            result = pd.concat(all_jobs, ignore_index=True)
            # Supprimer les doublons basés sur le titre + entreprise
            result = result.drop_duplicates(subset=['title', 'company'], keep='first')
            self.save_raw_data(result, "indeed")
            self.logger.info(f"Indeed RSS: {len(result)} offres extraites")
            return result
        
        return pd.DataFrame()

    def _extract_jobs_rss(self, country: str, query: str) -> pd.DataFrame:
        """Extrait les offres pour un pays et terme de recherche spécifiques"""
        if country not in self.base_urls:
            self.logger.warning(f"Pays non supporté: {country}")
            return pd.DataFrame()
        
        try:
            url = self.base_urls[country]
            params = {"q": query, "l": "", "format": "rss"}
            
            # Indeed RSS utilise des paramètres URL
            full_url = f"{url}?q={query}&format=rss"
            
            self.logger.debug(f"Extraction RSS: {full_url}")
            
            # Utiliser feedparser pour les flux RSS
            feed = feedparser.parse(full_url)
            
            if not feed.entries:
                self.logger.warning(f"Aucune entrée RSS pour {country}/{query}")
                return pd.DataFrame()
            
            jobs = []
            for entry in feed.entries[:50]:  # Limiter à 50 offres par flux
                # Extraire les informations de l'offre
                title = entry.get('title', '')
                description = entry.get('summary', '')
                link = entry.get('link', '')
                published = entry.get('published', '')
                
                # Extraire l'entreprise et la localisation du titre
                company = self._extract_company_from_title(title)
                location = self._extract_location_from_description(description)
                salary = self._extract_salary_from_description(description)
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description,
                    "salary": salary,
                    "url": link,
                    "published": published,
                    "country": country.upper(),
                    "search_term": query,
                    "source": "indeed_rss"
                })
            
            return pd.DataFrame(jobs)
            
        except Exception as e:
            self.logger.error(f"Erreur RSS Indeed {country}/{query}: {e}")
            return pd.DataFrame()

    def _extract_company_from_title(self, title: str) -> str:
        """Extrait le nom de l'entreprise du titre"""
        # Indeed format: "Job Title - Company Name"
        if " - " in title:
            parts = title.split(" - ")
            if len(parts) >= 2:
                return parts[-1].strip()
        return "Non spécifié"

    def _extract_location_from_description(self, description: str) -> str:
        """Extrait la localisation de la description"""
        # Patterns communs pour les localisations
        location_patterns = [
            r"Location:\s*([^<\n]+)",
            r"Lieu:\s*([^<\n]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*\d{5}",  # Ville, Code postal
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Non spécifié"

    def _extract_salary_from_description(self, description: str) -> str:
        """Extrait le salaire de la description"""
        # Patterns pour les salaires
        salary_patterns = [
            r"(\d+\s*(?:€|EUR|k€)(?:\s*-\s*\d+\s*(?:€|EUR|k€))?)",
            r"Salary:\s*([^<\n]+)",
            r"Salaire:\s*([^<\n]+)",
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Non spécifié" 