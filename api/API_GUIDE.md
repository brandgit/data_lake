# Guide d'utilisation de l'API JobTech Data Warehouse

Ce guide présente l'API JobTech mise à jour pour fonctionner avec le Data Warehouse PostgreSQL.

## 🚀 Vue d'ensemble

L'API JobTech fournit un accès RESTful aux données du marché de l'emploi tech, incluant :
- **Offres d'emploi** (Adzuna, RemoteOK)
- **Repositories GitHub** 
- **Tendances Google Trends**
- **Données développeurs** (StackOverflow)
- **Datasets salariaux** (Kaggle)

## 📋 Base URL

```
http://localhost:8000/api/v1/
```

## 🔐 Authentification

L'API utilise l'authentification par token ou session Django :

```bash
# Avec token
curl -H "Authorization: Token your-token-here" http://localhost:8000/api/v1/jobs/

# Avec authentification basique
curl -u username:password http://localhost:8000/api/v1/jobs/
```

## 📊 Endpoints principaux

### 🔍 Utilitaires

#### Health Check
```http
GET /v1/health/
```
Vérification de l'état de l'API.

#### Fraîcheur des données
```http
GET /v1/data-freshness/
```
Dernières dates de mise à jour pour chaque source.

#### Statistiques globales
```http
GET /v1/statistics/
```
Compteurs globaux de toutes les données.

### 📐 Tables de dimensions

#### Pays
```http
GET /v1/dimensions/countries/
GET /v1/dimensions/countries/{id_country}/
```

**Filtres disponibles :**
- `?search=france` - Recherche par nom ou code ISO
- `?ordering=country_name` - Tri

#### Entreprises
```http
GET /v1/dimensions/companies/
GET /v1/dimensions/companies/{id_company}/
```

**Filtres disponibles :**
- `?search=google` - Recherche par nom
- `?ordering=company_name` - Tri

#### Compétences
```http
GET /v1/dimensions/skills/
GET /v1/dimensions/skills/{id_skill}/
```

**Filtres disponibles :**
- `?skill_group=backend` - Filtrage par groupe
- `?search=python` - Recherche par libellé
- `?ordering=tech_label` - Tri

#### Sources de données
```http
GET /v1/dimensions/sources/
GET /v1/dimensions/sources/{id_source}/
```

### 💼 Tables de faits

#### Emplois
```http
GET /v1/jobs/
GET /v1/jobs/{id}/
```

**Filtres disponibles :**
- `?country=FR` - Filtrage par pays
- `?source=adzuna` - Filtrage par source
- `?contract_type=CDI` - Type de contrat
- `?search=python` - Recherche dans titre, description, technologies
- `?ordering=-salary_avg` - Tri par salaire décroissant

**Actions spécialisées :**
```http
GET /v1/jobs/by_country/          # Statistiques par pays
GET /v1/jobs/by_technology/?tech=python  # Analyse par technologie
```

#### Repositories GitHub
```http
GET /v1/github-repos/
GET /v1/github-repos/{repo_id}/
```

**Filtres disponibles :**
- `?language=Python` - Filtrage par langage
- `?search=machine` - Recherche dans nom/description
- `?ordering=-stars` - Tri par étoiles

**Actions spécialisées :**
```http
GET /v1/github-repos/top_languages/  # Top langages
```

#### Tendances Google
```http
GET /v1/google-trends/
GET /v1/google-trends/{id}/
```

**Filtres disponibles :**
- `?keyword=python` - Filtrage par mot-clé
- `?country=FR` - Filtrage par pays
- `?ordering=-date` - Tri par date

**Actions spécialisées :**
```http
GET /v1/google-trends/trending_now/        # Tendances actuelles
GET /v1/google-trends/top_technologies/    # Top 5 des technologies les plus utilisées
```

#### Développeurs
```http
GET /v1/developers/
GET /v1/developers/{respondent_id}/
```

**Filtres disponibles :**
- `?country=France` - Filtrage par pays
- `?employment=Employed` - Statut d'emploi
- `?remote_work=Remote` - Travail à distance
- `?search=python` - Recherche dans technologies/titre
- `?ordering=-salary` - Tri par salaire

**Actions spécialisées :**
```http
GET /v1/developers/salary_by_experience/           # Salaires par expérience
GET /v1/developers/average_salary_by_employment/   # Salaire moyen par type d'employment
GET /v1/developers/top_freelancer_job_titles/      # Job titles avec le plus de freelancers
GET /v1/developers/highest_paid_job_titles/        # Job titles les mieux payés
```

#### Datasets Kaggle
```http
GET /v1/kaggle-datasets/
GET /v1/kaggle-datasets/{id}/
```

**Filtres disponibles :**
- `?location=USA` - Filtrage par localisation
- `?search=data` - Recherche dans titre/technologies
- `?ordering=-salary` - Tri par salaire

**Actions spécialisées :**
```http
GET /v1/kaggle-datasets/best_paid_technology/  # Technologie la mieux payée
GET /v1/kaggle-datasets/junior_average_salary/ # Salaire moyen des juniors
```

### 🔗 Vues consolidées

#### Emplois consolidés
```http
GET /v1/jobs-consolidated/
GET /v1/jobs-consolidated/{unified_id}/
```

Vue unifiée combinant toutes les sources d'emplois.

## 📈 Endpoints d'analyse

### 💰 Analyse salariale
```http
GET /v1/analysis/salaries/?country=FR&technology=python
```

Compare les salaires entre différentes sources de données.

**Paramètres :**
- `country` - Code pays (optionnel)
- `technology` - Technologie (optionnel)

### 🔥 Tendances technologiques
```http
GET /v1/analysis/technology-trends/?tech=python
```

Analyse complète d'une technologie (emplois, GitHub, tendances, salaires).

**Paramètres requis :**
- `tech` - Nom de la technologie

### 🌍 Analyse par pays
```http
GET /v1/analysis/countries/?country=FR
```

Analyse complète d'un pays (emplois, salaires, technologies populaires).

**Paramètres requis :**
- `country` - Code pays (ISO2)

### 🏠 Analyse du travail à distance
```http
GET /v1/analysis/remote-work/
```

Statistiques sur les politiques de travail à distance.

## 📝 Exemples d'utilisation

### Rechercher des emplois Python en France
```bash
curl "http://localhost:8000/api/v1/jobs/?country=FR&search=python&ordering=-salary_avg"
```

### Obtenir les repositories GitHub les plus populaires en Python
```bash
curl "http://localhost:8000/api/v1/github-repos/?language=Python&ordering=-stars"
```

### Analyser les salaires des développeurs Python
```bash
curl "http://localhost:8000/api/v1/analysis/salaries/?technology=python"
```

### Voir les tendances actuelles
```bash
curl "http://localhost:8000/api/v1/google-trends/trending_now/"
```

### Top 5 des technologies Google Trends
```bash
curl "http://localhost:8000/api/v1/google-trends/top_technologies/"
```

### Salaire moyen par type d'employment
```bash
# Tous les types d'employment
curl "http://localhost:8000/api/v1/developers/average_salary_by_employment/"

# Employment spécifique
curl "http://localhost:8000/api/v1/developers/average_salary_by_employment/?employment=Freelancer"
```

### Job titles avec le plus de freelancers
```bash
curl "http://localhost:8000/api/v1/developers/top_freelancer_job_titles/"
```

### Job titles les mieux payés
```bash
curl "http://localhost:8000/api/v1/developers/highest_paid_job_titles/"
```

### Technologie la mieux payée (Kaggle)
```bash
curl "http://localhost:8000/api/v1/kaggle-datasets/best_paid_technology/"
```

### Salaire moyen des juniors (Kaggle)
```bash
curl "http://localhost:8000/api/v1/kaggle-datasets/junior_average_salary/"
```

## 📊 Format des réponses

### Listes paginées
```json
{
  "count": 1234,
  "next": "http://localhost:8000/api/v1/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": "job123",
      "title": "Python Developer",
      "company": "TechCorp",
      "salary_avg": 65000.00,
      "technologies_list": ["Python", "Django", "PostgreSQL"]
    }
  ]
}
```

### Objets individuels
```json
{
  "id": "job123",
  "title": "Python Developer",
  "company": "TechCorp",
  "location": "Paris, France",
  "country": "FR",
  "salary_min": 50000.00,
  "salary_max": 80000.00,
  "salary_avg": 65000.00,
  "description": "We are looking for...",
  "technologies": "Python, Django, PostgreSQL",
  "technologies_list": ["Python", "Django", "PostgreSQL"],
  "contract_type": "CDI",
  "source": "adzuna",
  "loaded_at": "2024-07-04T15:30:00Z"
}
```

### Analyses
```json
{
  "technology": "python",
  "job_count": 156,
  "avg_job_salary": 62000.00,
  "github_repos": 3421,
  "avg_trend_score": 85.5,
  "developer_count": 89,
  "avg_developer_salary": 75000.00
}
```

## ⚠️ Codes d'erreur

- `200` - Succès
- `400` - Requête invalide (paramètres manquants/incorrects)
- `401` - Non authentifié
- `403` - Accès refusé
- `404` - Ressource non trouvée
- `500` - Erreur serveur

## 🔧 Pagination

L'API utilise la pagination par défaut :
- **Taille de page par défaut :** 50 éléments
- **Taille maximum :** 500 éléments

Paramètres de pagination :
- `?page=2` - Page spécifique
- `?page_size=100` - Taille de page personnalisée

## 🎯 Filtres et recherche

### Filtres standards
- **Égalité exacte :** `?country=FR`
- **Inclusion :** `?country__in=FR,DE,IT`
- **Recherche texte :** `?search=python`

### Tri
- **Croissant :** `?ordering=salary_avg`
- **Décroissant :** `?ordering=-salary_avg`
- **Multiple :** `?ordering=-salary_avg,title`

## 📋 Test de l'API

Un script de test est disponible :

```bash
cd api/
python test_api.py
```

Ce script teste tous les endpoints et fournit un rapport de santé de l'API.

## 🚀 Démarrage rapide

1. **Démarrer l'API :**
```bash
cd api/
python manage.py runserver
```

2. **Tester la connexion :**
```bash
curl http://localhost:8000/api/v1/health/
```

3. **Obtenir les statistiques :**
```bash
curl http://localhost:8000/api/v1/statistics/
```

## 📞 Support

En cas de problème :
1. Vérifiez que la base de données PostgreSQL est accessible
2. Consultez les logs Django : `python manage.py runserver --verbosity=2`
3. Utilisez le script de test pour diagnostiquer : `python test_api.py` 