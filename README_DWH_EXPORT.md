# Export SQL Data Warehouse JobTech

## Description

Ce fichier contient l'export complet du Data Warehouse JobTech en format SQL. Il inclut la structure des tables et toutes les données chargées dans PostgreSQL.

## Fichiers

- **`jobtech_dwh_export.sql`** : Export complet du DWH (structure + données)
- **`export_dwh_sql.py`** : Script Python pour générer de nouveaux exports

## Contenu de l'Export

### Tables de Dimensions Exportées

| Table | Lignes | Description |
|-------|--------|-------------|
| `d_date` | 4,018 | Dimension temporelle (2020-2030) |
| `d_country` | 20 | Pays et codes ISO |
| `d_company` | 1 | Entreprises |
| `d_skill` | 919 | Compétences techniques |
| `d_source` | 6 | Sources de données |

### Tables de Faits

Les tables de faits suivantes sont définies dans le modèle mais n'étaient pas présentes lors de l'export :
- `job` : Offres d'emploi
- `github_repo` : Repositories GitHub
- `google_trend` : Tendances Google
- `developer` : Développeurs
- `kaggle_dataset` : Datasets Kaggle

### Vues

- **`jobs_consolidated`** : Vue consolidée joignant les emplois avec les dimensions

## Caractéristiques Techniques

- **Taille du fichier** : 0.20 MB
- **Encoding** : UTF-8
- **Lignes totales** : 5,095
- **Format** : PostgreSQL SQL
- **Date d'export** : 2025-07-05 17:27:41

## Utilisation

### Restaurer dans PostgreSQL

```bash
# Connexion à PostgreSQL
psql -h localhost -p 5432 -U jobtech_user -d jobtech_db

# Importer l'export
\i jobtech_dwh_export.sql
```

### Créer une nouvelle base

```bash
# Créer une nouvelle base
createdb -h localhost -p 5432 -U postgres jobtech_dwh_copy

# Importer dans la nouvelle base
psql -h localhost -p 5432 -U postgres -d jobtech_dwh_copy -f jobtech_dwh_export.sql
```

### Générer un nouvel export

```bash
# Exécuter le script d'export
python export_dwh_sql.py
```

## Structure des Tables

### Table `d_date` (Dimension Temporelle)
```sql
CREATE TABLE d_date (
    date_key DATE NOT NULL,
    day SMALLINT,
    month SMALLINT,
    quarter SMALLINT,
    year SMALLINT,
    day_week SMALLINT
);
```

### Table `d_country` (Pays)
```sql
CREATE TABLE d_country (
    country_id INTEGER NOT NULL,
    iso2 VARCHAR(2),
    country_name VARCHAR(255)
);
```

### Table `d_skill` (Compétences)
```sql
CREATE TABLE d_skill (
    skill_id INTEGER NOT NULL,
    tech_label VARCHAR(255),
    skill_group VARCHAR(255)
);
```

## Données Incluses

### Pays Disponibles (20)
- France (FR), Allemagne (DE), États-Unis (US)
- Royaume-Uni (GB), Canada (CA), Australie (AU)
- Et 14 autres pays

### Compétences (919)
- Langages : Python, JavaScript, Java, Go, etc.
- Frameworks : React, Django, Spring, etc.
- Technologies : Docker, Kubernetes, AWS, etc.
- Bases de données : PostgreSQL, MongoDB, etc.

### Sources de Données (6)
- Adzuna
- GitHub
- Google Trends
- Kaggle
- RemoteOK
- Stack Overflow

## Configuration

Le script utilise la configuration définie dans `config.py` :

```python
# Configuration PostgreSQL
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'jobtech_db'
DB_USER = 'jobtech_user'
DB_PASSWORD = 'jobtech_pass'
```

## ⚠️ Notes Importantes

1. **Limitation** : L'export limite les tables volumineuses à 10,000 lignes maximum
2. **Permissions** : Nécessite les droits de lecture sur la base PostgreSQL
3. **Mémoire** : Pour les gros volumes, l'export se fait par lots de 1,000 lignes
4. **Encoding** : Utilise UTF-8 pour supporter les caractères internationaux

## 🔄 Mise à Jour

Pour mettre à jour l'export après avoir chargé de nouvelles données :

```bash
# 1. Charger nouvelles données dans le DWH
python 01_scrape.py
python 02_clean.py
python 03_load_dwh.py

# 2. Générer nouvel export
python export_dwh_sql.py

# 3. Remplacer l'ancien export
mv jobtech_dwh_export_*.sql jobtech_dwh_export.sql
```