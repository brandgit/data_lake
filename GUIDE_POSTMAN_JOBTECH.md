# Guide d'Utilisation - Collection Postman JobTech API

## Configuration Initiale

### 1. Importer les Fichiers dans Postman

#### Collection
1. Ouvrez Postman
2. Cliquez sur **Import** (bouton en haut à gauche)
3. Sélectionnez le fichier `JobTech_API_Collection.postman_collection.json`
4. Cliquez sur **Import**

#### Environnement
1. Dans Postman, cliquez sur **Environments** (icône gear en haut à droite)
2. Cliquez sur **Import**
3. Sélectionnez le fichier `JobTech_API_Environment.postman_environment.json`
4. Cliquez sur **Import**
5. Sélectionnez l'environnement **"JobTech API - Environnement"** dans le menu déroulant

### 2. Variables d'Environnement

Les variables suivantes sont pré-configurées :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `base_url` | `http://localhost:8000/api/v1` | URL de base de l'API |
| `server_url` | `http://localhost:8000` | URL du serveur |
| `api_version` | `v1` | Version de l'API |
| `content_type` | `application/json` | Type de contenu |
| `pagination_limit` | `20` | Limite de pagination |
| `test_employment_type` | `Freelancer` | Type d'emploi pour les tests |
| `test_salary_min` | `50000` | Salaire minimum pour les tests |
| `test_salary_max` | `100000` | Salaire maximum pour les tests |
| `test_country_code` | `FR` | Code pays pour les tests |
| `test_skill_group` | `Programming Languages` | Groupe de compétences |

## 📂 Structure de la Collection

### Tests Simples (2 endpoints)
- **Test de Base** : Vérification basique de l'API
- **Health Check** : État de l'API et de la base de données

### Endpoints Spécifiques Demandés

#### Google Trends (3 endpoints)
- **Liste Google Trends** : Toutes les tendances
- **🎯 Top 5 Technologies** : Technologies les plus utilisées
- **🎯 Top Technologies par Intérêt Total** : Tri par intérêt total

#### Developers (6 endpoints)
- **Liste Developers** : Tous les développeurs
- **🎯 Salaire Moyen par Employment** : Analyse des salaires
- **🎯 Salaire Moyen des Freelancers** : Salaires spécifiques aux freelances
- **🎯 Job Titles avec Plus de Freelancers** : Postes avec plus de freelances
- **🎯 Job Titles les Mieux Payés** : Postes les mieux rémunérés
- **Développeurs Filtrés par Salaire** : Filtrage par fourchette

#### Kaggle Datasets (3 endpoints)
- **Liste Kaggle Datasets** : Tous les datasets
- **🎯 Technologie la Mieux Payée** : Analyse des technologies
- **🎯 Salaire Moyen des Juniors** : Salaires des juniors

### 📊 Tables de Dimensions (5 endpoints)
- **Dimension Dates** : Table temporelle
- **Dimension Pays** : Pays et codes ISO
- **Dimension Entreprises** : Entreprises référencées
- **Dimension Compétences** : Compétences techniques
- **Dimension Sources** : Sources de données

### 💼 Tables de Faits (6 endpoints)
- **Emplois** : Offres d'emploi
- **Repositories GitHub** : Dépôts GitHub
- **Google Trends** : Tendances de recherche
- **Développeurs** : Profils de développeurs
- **Datasets Kaggle** : Datasets Kaggle
- **Jobs Consolidés** : Vue consolidée avec dimensions

### 📈 Analyses et Statistiques (5 endpoints)
- **Analyse des Salaires** : Statistiques salariales
- **Analyse des Technologies** : Technologies populaires
- **Analyse par Pays** : Opportunités par pays
- **Analyse Travail Remote** : Opportunités télétravail
- **Statistiques Simples** : Métriques rapides

### 🔧 Utilitaires (2 endpoints)
- **Health Check** : État du système
- **Fraîcheur des Données** : Âge des données

## 📝 Ordre de Test Recommandé

### 1. Tests de Base
```
GET {{base_url}}/test/
GET {{base_url}}/health/
```

### 2. Endpoints Spécifiques Demandés
```
GET {{base_url}}/google-trends/top_technologies/
GET {{base_url}}/developers/average_salary_by_employment/
GET {{base_url}}/developers/top_freelancer_job_titles/
GET {{base_url}}/developers/highest_paid_job_titles/
GET {{base_url}}/kaggle-datasets/best_paid_technology/
GET {{base_url}}/kaggle-datasets/junior_average_salary/
```

### 3. Tables de Dimensions
```
GET {{base_url}}/d-dates/
GET {{base_url}}/d-countries/
GET {{base_url}}/d-companies/
GET {{base_url}}/d-skills/
GET {{base_url}}/d-sources/
```

### 4. Tables de Faits
```
GET {{base_url}}/jobs/
GET {{base_url}}/github-repos/
GET {{base_url}}/google-trends/
GET {{base_url}}/developers/
GET {{base_url}}/kaggle-datasets/
```

## 🎯 Réponses Attendues des Endpoints Demandés

### Google Trends - Top 5 Technologies
```json
{
  "message": "Top 5 technologies par différents critères",
  "data": {
    "total_interest": [
      {"keyword": "C++", "total_interest": 23661},
      {"keyword": "React", "total_interest": 22727},
      {"keyword": "MySQL", "total_interest": 21234},
      {"keyword": "Go", "total_interest": 21135},
      {"keyword": "AWS", "total_interest": 18092}
    ]
  }
}
```

### Developers - Salaire Moyen par Employment
```json
{
  "message": "Salaire moyen par type d'employment",
  "data": {
    "Freelancer": {
      "average_salary": 72321.67,
      "count": 93,
      "min_salary": 27310,
      "max_salary": 203803
    }
  }
}
```

### Developers - Job Titles avec Plus de Freelancers
```json
{
  "message": "Top job titles avec le plus de freelancers",
  "data": [
    {"job_title": "Desktop developer", "freelancer_count": 14},
    {"job_title": "Full-stack developer", "freelancer_count": 12},
    {"job_title": "Mobile developer", "freelancer_count": 11}
  ]
}
```

### Developers - Job Titles les Mieux Payés
```json
{
  "message": "Top job titles les mieux payés",
  "data": [
    {"job_title": "Cloud engineer", "average_salary": 93882.0},
    {"job_title": "System administrator", "average_salary": 89285.0},
    {"job_title": "Database administrator", "average_salary": 80011.0}
  ]
}
```

### Kaggle - Technologie la Mieux Payée
```json
{
  "message": "Technologies les mieux payées",
  "data": [
    {"technology": "Scala", "average_salary": 95000.0, "count": 15},
    {"technology": "Go", "average_salary": 87500.0, "count": 23}
  ]
}
```

### Kaggle - Salaire Moyen des Juniors
```json
{
  "message": "Salaire moyen des développeurs juniors",
  "data": {
    "average_salary": 45000.0,
    "count": 156,
    "min_salary": 28000,
    "max_salary": 65000
  }
}
```

## 🔧 Paramètres de Filtrage

### Pagination
Tous les endpoints supportent la pagination :
```
?page=1&limit=20
```

### Filtres Developers
```
?salary_min=50000&salary_max=100000
?employment_type=Freelancer
?job_title=Developer
?experience_years_min=2
?experience_years_max=5
```

### Filtres par Pays
```
?country=FR
?country=US,GB,DE
```

### Filtres par Compétences
```
?skill_group=Programming Languages
?tech_label=Python
```

## 🚨 Dépannage

### API Non Accessible
1. Vérifiez que l'API Django est démarrée :
   ```bash
   cd api/
   python manage.py runserver
   ```

2. Vérifiez l'URL dans l'environnement Postman :
   - `base_url` = `http://localhost:8000/api/v1`

### Erreurs 404
- Vérifiez que l'endpoint existe dans la collection
- Vérifiez l'orthographe de l'URL
- Consultez les logs Django pour plus de détails

### Données Vides
- Vérifiez que la base de données PostgreSQL est accessible
- Vérifiez que les données ont été chargées :
   ```bash
   python 01_scrape.py
   python 02_clean.py
   python 03_load_dwh.py
   ```

### Authentification
- L'authentification est **désactivée** pour tous les endpoints
- Aucun token ou header d'authentification requis

## 📊 Métriques et Monitoring

### Health Check
```json
{
  "status": "healthy",
  "timestamp": "2025-07-05T14:36:52.238587Z",
  "database": "connected",
  "version": "1.0.0"
}
```

### Fraîcheur des Données
```json
{
  "message": "Fraîcheur des données",
  "data": {
    "last_update": "2025-07-05T10:30:00Z",
    "tables_count": 10,
    "total_records": 9760
  }
}
```


## 🔄 Mise à Jour

Pour mettre à jour la collection après des modifications de l'API :

1. Re-exportez la collection depuis Postman
2. Mettez à jour les variables d'environnement si nécessaire
3. Testez les nouveaux endpoints ajoutés
4. Documentez les changements dans ce guide

---