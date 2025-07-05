

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from . import views

# Fonction simple pour test
def simple_test(request):
    return JsonResponse({
        "status": "success",
        "message": "API fonctionne !",
        "endpoints_disponibles": [
            "/api/v1/test/",
            "/api/v1/simple-stats/"
        ]
    })

def simple_stats(request):
    return JsonResponse({
        "message": "Statistiques simples",
        "total_jobs": 1000,
        "total_developers": 500,
        "technologies": ["Python", "JavaScript", "React", "Django"]
    })

# Créer un routeur
router = DefaultRouter()

# =================
# VIEWSETS DES DIMENSIONS
# =================
router.register(r'dimensions/countries', views.DCountryViewSet, basename='d-countries')
router.register(r'dimensions/companies', views.DCompanyViewSet, basename='d-companies')
router.register(r'dimensions/skills', views.DSkillViewSet, basename='d-skills')
router.register(r'dimensions/sources', views.DSourceViewSet, basename='d-sources')

# =================
# VIEWSETS DES TABLES DE FAITS
# =================
router.register(r'jobs', views.JobViewSet, basename='jobs')
router.register(r'github-repos', views.GitHubRepoViewSet, basename='github-repos')
router.register(r'google-trends', views.GoogleTrendViewSet, basename='google-trends')
router.register(r'developers', views.DeveloperViewSet, basename='developers')
router.register(r'kaggle-datasets', views.KaggleDatasetViewSet, basename='kaggle-datasets')

# =================
# VUES CONSOLIDÉES
# =================
router.register(r'jobs-consolidated', views.JobsConsolidatedViewSet, basename='jobs-consolidated')

# URLs de l'API
urlpatterns = [
    # ENDPOINTS SIMPLES POUR TEST POSTMAN
    path('v1/test/', simple_test, name='simple-test'),
    path('v1/simple-stats/', simple_stats, name='simple-stats'),
    
    # Router URLs
    path('v1/', include(router.urls)),
    
    # =================
    # ENDPOINTS D'ANALYSE ET STATISTIQUES
    # =================
    
    # Statistiques globales
    path('v1/statistics/', views.StatisticsView.as_view(), name='global-statistics'),
    
    # Analyses salariales
    path('v1/analysis/salaries/', views.SalaryAnalysisView.as_view(), name='salary-analysis'),
    
    # Analyses technologiques
    path('v1/analysis/technology-trends/', views.TechnologyTrendsView.as_view(), name='technology-trends'),
    
    # Analyses par pays
    path('v1/analysis/countries/', views.CountryAnalysisView.as_view(), name='country-analysis'),
    
    # Analyses du travail à distance
    path('v1/analysis/remote-work/', views.RemoteWorkAnalysisView.as_view(), name='remote-work-analysis'),
    
    # =================
    # ENDPOINTS UTILITAIRES
    # =================
    
    # Vérifications système
    path('v1/health/', views.health_check, name='health-check'),
    path('v1/data-freshness/', views.data_freshness, name='data-freshness'),
] 