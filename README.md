# JobTech - Projet Data Warehouse & API

## Description

JobTech est un projet complet de Data Warehouse analysant le marché de l'emploi dans le domaine technologique. Il combine extraction de données, nettoyage, chargement en base PostgreSQL, et exposition via une API Django REST.

## Architecture du Projet

```
project/
├── PIPELINE ETL
│   ├── 01_scrape.py              # Extraction des données
│   ├── 02_clean.py               # Nettoyage et transformation
│   ├── 03_load_dwh.py            # Chargement en Data Warehouse
│   └── config.py                 # Configuration globale
├── UTILITAIRES
│   ├── utils/                    # Modules utilitaires
│   │   ├── extract/              # Extracteurs de données
│   │   ├── clean/                # Nettoyeurs de données
│   │   └── load/                 # Chargeurs de données
├── API REST
│   ├── api/                      # Application Django
│   │   ├── jobtech_api/          # App principale
│   │   ├── manage.py             # Gestionnaire Django
│   │   ├── requirements.txt      # Dépendances Python
│   │   └── docker-compose.yml    # Configuration Docker
├── DONNÉES
│   ├── raw/                      # Données brutes
│   ├── datasets_clean/           # Données nettoyées
├── EXPORTS
│   ├── jobtech_dwh_export.sql    # Export SQL du DWH
│   ├── JobTech_API_Collection.postman_collection.json
│   └── JobTech_API_Environment.postman_environment.json
└── DOCUMENTATION
    ├── README.md                 # Ce fichier
    ├── README_DWH_EXPORT.md     # Documentation export SQL
    ├── GUIDE_POSTMAN_JOBTECH.md # Guide API Postman
    └── README_EXPORTS.md        # Récapitulatif des exports
```

## Prérequis

### Logiciels Requis
- **Python 3.10+** avec pip
- **PostgreSQL 12+** (ou Docker)
- **Postman** (pour tester l'API)

### Dépendances Python
```bash
# Installation des dépendances principales
pip install pandas numpy requests beautifulsoup4 psycopg2-binary

# Pour l'API Django
pip install django djangorestframework django-cors-headers
```

## Installation et Lancement

### 1. Configuration de l'Environnement

#### Cloner et Préparer le Projet
```bash
# Cloner le projet
git clone https://github.com/brandgit/jobtech.git
cd jobtech

# Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r api/requirements.txt
```

#### Configuration de la Base de Données
```bash
# Option 1: PostgreSQL local
createdb jobtech_db
psql -d jobtech_db -c "CREATE USER jobtech_user WITH PASSWORD 'jobtech_pass';"
psql -d jobtech_db -c "GRANT ALL PRIVILEGES ON DATABASE jobtech_db TO jobtech_user;"

# Option 2: Docker PostgreSQL
cd api/
docker-compose up -d db
```

### 2. Pipeline ETL - Extraction et Chargement des Données

#### Étape 1: Extraction des Données
```bash
# Lancer l'extraction depuis les sources
python 01_scrape.py

# Vérifier les données extraites
ls -la raw/
```

#### Étape 2: Nettoyage et Transformation
```bash
# Nettoyer et transformer les données
python 02_clean.py

# Vérifier les données nettoyées
ls -la datasets_clean/
```

#### Étape 3: Chargement en Data Warehouse
```bash
# Charger les données dans PostgreSQL
python 03_load_dwh.py

# Vérifier le chargement
psql -h localhost -p 5432 -U jobtech_user -d jobtech_db -c "SELECT COUNT(*) FROM d_skill;"
```

### 3. Lancement de l'API Django

#### Préparer l'API
```bash
# Aller dans le dossier API
cd api/

# Appliquer les migrations Django
python manage.py migrate

# Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

#### Vérifier l'API
```bash
# Tester l'API avec curl
curl http://localhost:8000/api/v1/health/

# Réponse attendue:
# {"status":"healthy","timestamp":"2025-07-05T...","database":"connected"}
```

### 4. Utilisation avec Postman

#### Importer les Collections
1. Ouvrir Postman
2. Importer `JobTech_API_Collection.postman_collection.json`
3. Importer `JobTech_API_Environment.postman_environment.json`
4. Sélectionner l'environnement "JobTech API - Environnement"

#### Tester les Endpoints Prioritaires
```bash
# Endpoints spécifiques demandés 
GET /api/v1/google-trends/top_technologies/
GET /api/v1/developers/average_salary_by_employment/
GET /api/v1/developers/top_freelancer_job_titles/
GET /api/v1/developers/highest_paid_job_titles/
GET /api/v1/kaggle-datasets/best_paid_technology/
GET /api/v1/kaggle-datasets/junior_average_salary/
```

## Utilisation des Scripts

### Scripts Principaux

#### `01_scrape.py` - Extraction
```bash
# Extraction complète
python 01_scrape.py

# Extraction sélective (par source)
python 01_scrape.py --source adzuna
python 01_scrape.py --source github
```

#### `02_clean.py` - Nettoyage
```bash
# Nettoyage complet
python 02_clean.py

# Nettoyage par type de données
python 02_clean.py --type jobs
python 02_clean.py --type skills
```

#### `03_load_dwh.py` - Chargement
```bash
# Chargement complet
python 03_load_dwh.py

# Chargement par table
python 03_load_dwh.py --table d_skill
python 03_load_dwh.py --table d_country
```

### Scripts d'Export

#### Export SQL du Data Warehouse
```bash
# Générer un export SQL complet
python export_dwh_sql.py

# Fichier généré: jobtech_dwh_export_YYYYMMDD_HHMMSS.sql
```

#### Test de l'API
```bash
# Tester tous les endpoints
cd api/
python test_api.py

# Tester endpoints spécifiques
python test_api.py --endpoint health
python test_api.py --endpoint google-trends
```

## Endpoints API Disponibles

### Tests et Monitoring
- `GET /api/v1/test/` - Test de base
- `GET /api/v1/health/` - État de l'API
- `GET /api/v1/data-freshness/` - Fraîcheur des données

### Endpoints Spécifiques Demandés
- `GET /api/v1/google-trends/top_technologies/` - Top 5 technologies
- `GET /api/v1/developers/average_salary_by_employment/` - Salaires par employment
- `GET /api/v1/developers/top_freelancer_job_titles/` - Top jobs freelance
- `GET /api/v1/developers/highest_paid_job_titles/` - Jobs les mieux payés
- `GET /api/v1/kaggle-datasets/best_paid_technology/` - Techno mieux payée
- `GET /api/v1/kaggle-datasets/junior_average_salary/` - Salaire moyen junior

### Tables de Données
- `GET /api/v1/d-dates/` - Dimension temporelle
- `GET /api/v1/d-countries/` - Pays
- `GET /api/v1/d-skills/` - Compétences
- `GET /api/v1/jobs/` - Offres d'emploi
- `GET /api/v1/developers/` - Développeurs
- `GET /api/v1/google-trends/` - Tendances Google

## Données Disponibles

### Sources de Données
- **Adzuna** : Offres d'emploi
- **GitHub** : Repositories et trends
- **Google Trends** : Tendances de recherche
- **Kaggle** : Datasets et salaires
- **RemoteOK** : Emplois remote
- **Stack Overflow** : Enquêtes développeurs

### Métriques Actuelles
- **Tables de dimensions** : 5 tables (4,964 lignes)
- **Compétences** : 919 technologies référencées
- **Pays** : 20 pays couverts
- **Période** : 2020-2030 (dimension temporelle)

## Maintenance et Mise à Jour

### Mise à Jour des Données
```bash
# Pipeline complet de mise à jour
python 01_scrape.py    # Nouvelles données
python 02_clean.py     # Nettoyage
python 03_load_dwh.py  # Chargement

# Redémarrer l'API
cd api/
python manage.py runserver
```

### Sauvegarde et Restauration
```bash
# Sauvegarder le Data Warehouse
python export_dwh_sql.py
# Génère: jobtech_dwh_export_YYYYMMDD_HHMMSS.sql

# Restaurer depuis une sauvegarde
psql -h localhost -p 5432 -U jobtech_user -d jobtech_db -f jobtech_dwh_export.sql
```

### Monitoring
```bash
# Vérifier l'état de l'API
curl http://localhost:8000/api/v1/health/

# Vérifier les logs
tail -f api/logs/django.log

# Vérifier la base de données
psql -h localhost -p 5432 -U jobtech_user -d jobtech_db -c "SELECT COUNT(*) FROM d_skill;"
```

## Dépannage

### Problèmes Courants

#### Base de Données Non Accessible
```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # Mac

# Vérifier la connexion
psql -h localhost -p 5432 -U jobtech_user -d jobtech_db -c "SELECT version();"
```

#### API Non Accessible
```bash
# Vérifier que l'API est démarrée
curl http://localhost:8000/api/v1/health/

# Vérifier les logs Django
cd api/
python manage.py runserver --verbosity=2
```

#### Données Manquantes
```bash
# Vérifier les données brutes
ls -la raw/

# Vérifier les données nettoyées
ls -la datasets_clean/

# Vérifier les tables en base
psql -h localhost -p 5432 -U jobtech_user -d jobtech_db -c "\dt"
```

### Logs et Debugging
```bash
# Activer le debug Django
cd api/
export DJANGO_DEBUG=True
python manage.py runserver

# Vérifier les logs ETL
tail -f data_pipeline.log

# Vérifier les requêtes SQL
psql -h localhost -p 5432 -U jobtech_user -d jobtech_db -c "SELECT pg_stat_activity.query FROM pg_stat_activity;"
```


# Test des endpoints avec curl
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/google-trends/top_technologies/
```

## Ordre de Lancement Recommandé

### 1. Première Installation
```bash
# 1. Préparer l'environnement
python -m venv venv
source venv/bin/activate
pip install -r api/requirements.txt

# 2. Configurer la base de données
createdb jobtech_db
# ou docker-compose up -d db

# 3. Lancer le pipeline ETL
python 01_scrape.py
python 02_clean.py  
python 03_load_dwh.py

# 4. Préparer l'API
cd api/
python manage.py migrate
python manage.py runserver

# 5. Tester avec Postman
# Importer les collections et tester les endpoints
```

### 2. Utilisation Quotidienne
```bash
# 1. Mettre à jour les données
python 01_scrape.py
python 02_clean.py
python 03_load_dwh.py

# 2. Lancer l'API
cd api/
python manage.py runserver

# 3. Utiliser l'API
curl http://localhost:8000/api/v1/health/
```

## Documentation

- **`README.md`** : Ce fichier (guide principal)
- **`README_DWH_EXPORT.md`** : Documentation de l'export SQL
- **`GUIDE_POSTMAN_JOBTECH.md`** : Guide d'utilisation Postman
- **`README_EXPORTS.md`** : Récapitulatif des exports
- **`api/README.md`** : Documentation spécifique de l'API



## Résultats Attendus

Après avoir suivi ce guide, vous devriez avoir :

✅ **Data Warehouse** : Base PostgreSQL avec 5 tables de dimensions  
✅ **API REST** : 32 endpoints disponibles  
✅ **6 Endpoints spécifiques** : Analyses demandées fonctionnelles  
✅ **Collection Postman** : Tests API prêts à l'emploi  
✅ **Export SQL** : Sauvegarde complète du DWH  
✅ **Pipeline ETL** : Automatisation extraction → nettoyage → chargement  

---

**🚀 Projet JobTech - Version 1.0**  
**📅 Dernière mise à jour** : 2025-07-05  
**👥 Équipe** : Data Engineering & API Development  
**📊 Données** : 4,964 enregistrements chargés  
**🎯 Endpoints** : 32 endpoints, 6 spécifiques opérationnels 