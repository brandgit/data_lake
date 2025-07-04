#!/usr/bin/env python3
"""
Script de test pour l'API JobTech après mise à jour vers le DWH PostgreSQL

Ce script teste tous les endpoints principaux de l'API pour s'assurer
qu'elle fonctionne correctement avec la nouvelle base de données.
"""

import os
import sys
import requests
import json
from requests.auth import HTTPBasicAuth

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"  # À modifier selon votre config
PASSWORD = "admin"  # À modifier selon votre config


def test_endpoint(url, auth=None, params=None):
    """Teste un endpoint de l'API"""
    try:
        response = requests.get(url, auth=auth, params=params, timeout=10)
        return {
            'url': url,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'data_count': len(response.json().get('results', response.json())) if response.status_code == 200 else 0,
            'error': None
        }
    except Exception as e:
        return {
            'url': url,
            'status_code': None,
            'success': False,
            'data_count': 0,
            'error': str(e)
        }


def main():
    """Fonction principale de test"""
    print("🚀 Test de l'API JobTech Data Warehouse")
    print("=" * 50)
    
    # Authentification (optionnelle selon config)
    auth = HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME and PASSWORD else None
    
    # Liste des endpoints à tester
    endpoints_to_test = [
        # Utilitaires
        ("Health Check", f"{API_BASE_URL}/health/"),
        ("Data Freshness", f"{API_BASE_URL}/data-freshness/"),
        ("Global Statistics", f"{API_BASE_URL}/statistics/"),
        
        # Dimensions
        ("Countries", f"{API_BASE_URL}/dimensions/countries/"),
        ("Companies", f"{API_BASE_URL}/dimensions/companies/"),
        ("Skills", f"{API_BASE_URL}/dimensions/skills/"),
        ("Sources", f"{API_BASE_URL}/dimensions/sources/"),
        
        # Tables de faits
        ("Jobs", f"{API_BASE_URL}/jobs/"),
        ("GitHub Repos", f"{API_BASE_URL}/github-repos/"),
        ("Google Trends", f"{API_BASE_URL}/google-trends/"),
        ("Developers", f"{API_BASE_URL}/developers/"),
        ("Kaggle Datasets", f"{API_BASE_URL}/kaggle-datasets/"),
        
        # Vues consolidées
        ("Jobs Consolidated", f"{API_BASE_URL}/jobs-consolidated/"),
        
        # Analyses
        ("Salary Analysis", f"{API_BASE_URL}/analysis/salaries/"),
        ("Technology Trends", f"{API_BASE_URL}/analysis/technology-trends/", {"tech": "python"}),
        ("Country Analysis", f"{API_BASE_URL}/analysis/countries/", {"country": "FR"}),
        ("Remote Work Analysis", f"{API_BASE_URL}/analysis/remote-work/"),
    ]
    
    # Tests spécialisés pour les actions des viewsets
    action_endpoints = [
        ("Jobs by Country", f"{API_BASE_URL}/jobs/by_country/"),
        ("Jobs by Technology", f"{API_BASE_URL}/jobs/by_technology/", {"tech": "python"}),
        ("GitHub Top Languages", f"{API_BASE_URL}/github-repos/top_languages/"),
        ("Google Trending Now", f"{API_BASE_URL}/google-trends/trending_now/"),
        ("Google Top Technologies", f"{API_BASE_URL}/google-trends/top_technologies/"),
        ("Developer Salary by Experience", f"{API_BASE_URL}/developers/salary_by_experience/"),
        ("Developer Average Salary by Employment", f"{API_BASE_URL}/developers/average_salary_by_employment/"),
        ("Developer Salary for Freelancers", f"{API_BASE_URL}/developers/average_salary_by_employment/", {"employment": "Freelancer"}),
        ("Top Freelancer Job Titles", f"{API_BASE_URL}/developers/top_freelancer_job_titles/"),
        ("Highest Paid Job Titles", f"{API_BASE_URL}/developers/highest_paid_job_titles/"),
        ("Kaggle Best Paid Technology", f"{API_BASE_URL}/kaggle-datasets/best_paid_technology/"),
        ("Kaggle Junior Average Salary", f"{API_BASE_URL}/kaggle-datasets/junior_average_salary/"),
    ]
    
    results = []
    
    # Test des endpoints principaux
    print("\n📊 Test des endpoints principaux:")
    for name, url, *params in endpoints_to_test:
        params = params[0] if params else None
        result = test_endpoint(url, auth=auth, params=params)
        results.append((name, result))
        
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {name}: {result['status_code']} - {result['data_count']} éléments")
        
        if result['error']:
            print(f"   ⚠️  Erreur: {result['error']}")
    
    # Test des actions spécialisées
    print("\n🔍 Test des actions spécialisées:")
    for name, url, *params in action_endpoints:
        params = params[0] if params else None
        result = test_endpoint(url, auth=auth, params=params)
        results.append((name, result))
        
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {name}: {result['status_code']} - {result['data_count']} éléments")
        
        if result['error']:
            print(f"   ⚠️  Erreur: {result['error']}")
    
    # Résumé final
    print("\n📈 Résumé des tests:")
    print("=" * 30)
    
    successful_tests = sum(1 for _, result in results if result['success'])
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"Tests réussis: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 Tous les tests sont passés ! L'API fonctionne parfaitement.")
    elif success_rate >= 80:
        print("✅ La plupart des tests sont passés. Quelques ajustements peuvent être nécessaires.")
    else:
        print("⚠️  Plusieurs tests ont échoué. Vérifiez la configuration et la base de données.")
    
    # Tests de données spécifiques
    print("\n🔎 Vérification des données:")
    
    # Test statistiques globales
    stats_result = test_endpoint(f"{API_BASE_URL}/statistics/", auth=auth)
    if stats_result['success']:
        try:
            response = requests.get(f"{API_BASE_URL}/statistics/", auth=auth)
            stats = response.json()
            print(f"📊 Jobs: {stats.get('total_jobs', 0)}")
            print(f"📊 GitHub Repos: {stats.get('total_github_repos', 0)}")
            print(f"📊 Google Trends: {stats.get('total_trends', 0)}")
            print(f"📊 Developers: {stats.get('total_developers', 0)}")
            print(f"📊 Kaggle Datasets: {stats.get('total_kaggle_datasets', 0)}")
            print(f"📊 Companies: {stats.get('total_companies', 0)}")
            print(f"📊 Skills: {stats.get('total_skills', 0)}")
            print(f"📊 Countries: {stats.get('total_countries', 0)}")
        except:
            pass
    
    print("\n" + "=" * 50)
    return success_rate == 100


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 