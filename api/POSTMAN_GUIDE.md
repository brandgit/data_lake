# Guide Postman - JobTech API

Ce guide vous explique comment utiliser la collection Postman pour tester les endpoints spécifiques demandés.

## 🚀 Installation

1. **Importer la collection :**
   - Ouvrez Postman
   - Cliquez sur "Import"
   - Sélectionnez le fichier `JobTech_API_Postman_Collection.json`

2. **Configurer l'URL de base :**
   - La variable `{{base_url}}` est définie sur `http://localhost:8000/api/v1`
   - Modifiez-la si votre API tourne sur un autre port

3. **Configuration de l'authentification :**
   - L'authentification basique est préconfigurée avec `admin:admin`
   - Modifiez les credentials dans l'onglet "Authorization" si nécessaire

## 📊 Endpoints Spécifiques Demandés

### 🔍 Google Trends

#### **Top 5 des Technologies les Plus Utilisées**
```
GET {{base_url}}/google-trends/top_technologies/
```

**Réponse attendue :**
```json
{
  "message": "Top 5 des technologies les plus utilisées",
  "data": [
    {
      "keyword": "python",
      "total_interest": 15420,
      "avg_interest": 85.5,
      "count_entries": 180
    },
    // ... 4 autres technologies
  ]
}
```

### 👨‍💻 Developers

#### **1. Salaire Moyen par Type d'Employment**
```
GET {{base_url}}/developers/average_salary_by_employment/
```

**Réponse :** Liste de tous les types d'employment avec salaires moyens

#### **2. Salaire Moyen d'un Employment Spécifique**
```
GET {{base_url}}/developers/average_salary_by_employment/?employment=Freelancer
```

**Paramètres disponibles :**
- `employment=Freelancer`
- `employment=Employed`
- `employment=Self-employed`
- etc.

**Réponse attendue :**
```json
{
  "message": "Salaire moyen pour employment: Freelancer",
  "employment": "Freelancer",
  "data": {
    "avg_salary": 75000.50,
    "count": 45,
    "min_salary": 35000.00,
    "max_salary": 150000.00
  }
}
```

#### **3. Job Title avec le Plus de Freelancers**
```
GET {{base_url}}/developers/top_freelancer_job_titles/
```

**Réponse attendue :**
```json
{
  "message": "Job titles avec le plus de freelancers",
  "data": [
    {
      "job_title": "Web Developer",
      "freelancer_count": 25,
      "avg_salary": 65000.00
    },
    // ... autres job titles
  ]
}
```

#### **4. Job Title le Mieux Payé**
```
GET {{base_url}}/developers/highest_paid_job_titles/
```

**Réponse attendue :**
```json
{
  "message": "Job titles les mieux payés",
  "data": [
    {
      "job_title": "Principal Software Engineer",
      "avg_salary": 145000.00,
      "max_salary": 200000.00,
      "count": 12
    },
    // ... autres job titles
  ]
}
```

### 📈 Kaggle Datasets

#### **1. Technologie la Mieux Payée**
```
GET {{base_url}}/kaggle-datasets/best_paid_technology/
```

**Réponse attendue :**
```json
{
  "message": "Technologies les mieux payées (Kaggle)",
  "data": [
    {
      "technology": "machine learning",
      "avg_salary": 98500.00,
      "max_salary": 150000.00,
      "min_salary": 60000.00,
      "count": 45
    },
    // ... autres technologies
  ]
}
```

#### **2. Salaire Moyen d'un Junior**
```
GET {{base_url}}/kaggle-datasets/junior_average_salary/
```

**Réponse attendue :**
```json
{
  "message": "Salaire moyen des juniors (≤2 ans d'expérience)",
  "global_stats": {
    "avg_salary": 52000.00,
    "min_salary": 35000.00,
    "max_salary": 75000.00,
    "count": 120
  },
  "by_experience_years": [
    {
      "experience_years": 0,
      "avg_salary": 45000.00,
      "count": 30
    },
    {
      "experience_years": 1,
      "avg_salary": 50000.00,
      "count": 45
    },
    {
      "experience_years": 2,
      "avg_salary": 58000.00,
      "count": 35
    }
  ]
}
```

## 🎯 Collection Postman - Organisation

### **📊 Google Trends - Endpoints Demandés**
- ✅ Top 5 des Technologies les Plus Utilisées
- ✅ Tendances Actuelles

### **👨‍💻 Developers - Endpoints Demandés**  
- ✅ Salaire Moyen par Type d'Employment
- ✅ Salaire Moyen d'un Employment Spécifique
- ✅ Job Title avec le Plus de Freelancers
- ✅ Job Title le Mieux Payé
- ✅ Salaires par Niveau d'Expérience

### **📈 Kaggle Datasets - Endpoints Demandés**
- ✅ Technologie la Mieux Payée  
- ✅ Salaire Moyen d'un Junior

### **💼 Tables de Faits** (données brutes)
- Emplois
- GitHub Repos  
- Google Trends
- Developers
- Kaggle Datasets

### **📐 Tables de Dimensions**
- Pays
- Entreprises
- Compétences  
- Sources

### **📈 Analyses Avancées**
- Analyse Salariale
- Tendances Technologiques
- Analyse par Pays
- Analyse Travail à Distance

## ⚡ Test Rapide

1. **Démarrer l'API :**
```bash
cd api/
python manage.py runserver
```

2. **Dans Postman :**
   - Importer la collection
   - Tester d'abord "Health Check" 
   - Puis tester les endpoints spécifiques dans l'ordre suivant :

### **Ordre de test recommandé :**

1. **🔍 Utilitaires**
   - Health Check → Vérifier que l'API répond
   - Statistiques Globales → Voir les volumes de données

2. **📊 Google Trends**  
   - Top 5 des Technologies → Votre endpoint principal

3. **👨‍💻 Developers**
   - Salaire Moyen par Type d'Employment → Vue globale
   - Salaire Moyen Freelancer → Cas spécifique
   - Top Freelancer Job Titles → Analyse freelance
   - Job Titles Mieux Payés → Analyse salaires

4. **📈 Kaggle**
   - Technologie Mieux Payée → Technologies valorisées
   - Salaire Moyen Junior → Analyse débutants

## 🛠️ Troubleshooting

**Erreur 500 :** Vérifiez que PostgreSQL est démarré et que les données sont chargées
**Erreur 401 :** Vérifiez les credentials d'authentification  
**Erreur 404 :** Vérifiez l'URL et que l'API est démarrée
**Pas de données :** Exécutez d'abord le script de chargement DWH

## 📞 Support

En cas de problème :
1. Vérifiez les logs Django : `python manage.py runserver --verbosity=2`
2. Testez avec le script automatique : `python test_api.py`
3. Consultez le guide API complet : `API_GUIDE.md` 