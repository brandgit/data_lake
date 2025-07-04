# JobTech API

API REST Django pour accéder aux données du marché de l'emploi tech.

## 🚀 Démarrage rapide

### Avec Docker (recommandé)

```bash
# Démarrer tous les services
docker-compose up -d

# L'API sera disponible sur http://localhost:8000
```

### Installation locale

```bash
cd api
pip install -r requirements.txt
python manage.py migrate
python manage.py create_api_token admin --create-user
python manage.py runserver
```

## 📚 Documentation

- **Interface Swagger** : http://localhost:8000/api/docs/
- **Interface ReDoc** : http://localhost:8000/api/redoc/
- **Admin Django** : http://localhost:8000/admin/

## 🔐 Authentification

L'API utilise l'authentification par token. Pour obtenir un token :

```bash
# Créer un utilisateur et son token
python manage.py create_api_token mon_utilisateur --create-user

# Utiliser le token dans les requêtes
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/v1/jobs/
```

## 📊 Endpoints disponibles

### Endpoints principaux

- `GET /api/v1/companies/` - Liste des entreprises
- `GET /api/v1/jobs/` - Liste des offres d'emploi
- `GET /api/v1/skills/` - Liste des compétences
- `GET /api/v1/trends/` - Données des tendances
- `GET /api/v1/salaries/` - Données des salaires

### Endpoints statistiques

- `GET /api/v1/statistics/` - Statistiques globales
- `GET /api/v1/salary-stats/?country=FR&skill=python` - Stats salariales
- `GET /api/v1/top-skills/` - Top des compétences
- `GET /api/v1/skill-trends/` - Tendances des compétences

## 🔍 Filtres et recherche

### Filtres pour les jobs

```bash
# Par pays
GET /api/v1/jobs/?country=FR

# Par compétences
GET /api/v1/jobs/?skills=python,django

# Par salaire
GET /api/v1/jobs/?salary_min=40000&salary_max=80000

# Par type de contrat
GET /api/v1/jobs/?contract_type=full_time

# Par niveau d'expérience
GET /api/v1/jobs/?experience_level=senior

# Recherche textuelle
GET /api/v1/jobs/?search=développeur
```

### Filtres pour les entreprises

```bash
# Par pays
GET /api/v1/companies/?country=FR

# Recherche par nom
GET /api/v1/companies/?search=Google
```

## 📄 Pagination

Toutes les listes sont paginées :

```json
{
  "count": 1250,
  "next": "http://localhost:8000/api/v1/jobs/?page=2",
  "previous": null,
  "results": [...]
}
```

## 🛠️ Variables d'environnement

```env
# Base de données
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=jobtech_db
POSTGRES_USER=jobtech_user
POSTGRES_PASSWORD=jobtech_pass

# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
```

## 🧪 Tests

```bash
# Lancer les tests
python manage.py test

# Avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Structure du projet

```
api/
├── api_project/          # Configuration Django
│   ├── settings.py       # Paramètres
│   ├── urls.py          # URLs principales
│   └── wsgi.py          # WSGI
├── jobtech_api/         # Application principale
│   ├── models.py        # Modèles de données
│   ├── serializers.py   # Serializers DRF
│   ├── views.py         # Vues API
│   ├── urls.py          # URLs de l'API
│   ├── filters.py       # Filtres
│   └── admin.py         # Interface admin
├── requirements.txt     # Dépendances
├── Dockerfile          # Image Docker
└── manage.py           # Commandes Django
``` 