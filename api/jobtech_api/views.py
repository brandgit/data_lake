

from rest_framework import viewsets, status, filters, views
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Min, Max, F, Sum
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
from collections import defaultdict
import logging

from .models import (
    # Tables de dimensions
    DDate, DCountry, DCompany, DSkill, DSource,
    # Tables de faits
    Job, GitHubRepo, GoogleTrend, Developer, KaggleDataset,
    # Vues
    JobsConsolidated
)
from .serializers import (
    # Dimensions
    DDateSerializer, DCountrySerializer, DCompanySerializer,
    DSkillSerializer, DSourceSerializer,
    # Tables de faits
    JobListSerializer, JobDetailSerializer,
    GitHubRepoListSerializer, GitHubRepoDetailSerializer,
    GoogleTrendSerializer,
    DeveloperListSerializer, DeveloperDetailSerializer,
    KaggleDatasetSerializer, JobsConsolidatedSerializer,
    # Statistiques
    StatisticsSerializer, SalaryStatsSerializer,
    TechnologyStatsSerializer, CountryStatsSerializer,
    TrendAnalysisSerializer, ExperienceStatsSerializer,
    CompanyStatsSerializer, SkillDemandSerializer,
    RemoteWorkStatsSerializer
)

logger = logging.getLogger('jobtech_api')


# =================
# VIEWSETS DES DIMENSIONS
# =================

class DCountryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les pays"""
    queryset = DCountry.objects.all()
    serializer_class = DCountrySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['country_name', 'iso2']
    ordering_fields = ['country_name']
    ordering = ['country_name']


class DCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les entreprises"""
    queryset = DCompany.objects.all()
    serializer_class = DCompanySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name']
    ordering_fields = ['company_name']
    ordering = ['company_name']


class DSkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les compétences"""
    queryset = DSkill.objects.all()
    serializer_class = DSkillSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['skill_group']
    search_fields = ['tech_label']
    ordering_fields = ['tech_label', 'skill_group']
    ordering = ['tech_label']


class DSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les sources de données"""
    queryset = DSource.objects.all()
    serializer_class = DSourceSerializer


# =================
# VIEWSETS DES TABLES DE FAITS
# =================

class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les offres d'emploi"""
    queryset = Job.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'source', 'contract_type']
    search_fields = ['title', 'description', 'company', 'technologies']
    ordering_fields = ['loaded_at', 'salary_avg', 'salary_min', 'salary_max']
    ordering = ['-loaded_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobDetailSerializer

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Emplois par pays"""
        country_stats = Job.objects.values('country').annotate(
            count=Count('id'),
            avg_salary=Avg('salary_avg')
        ).order_by('-count')
        return Response(country_stats)

    @action(detail=False, methods=['get'])
    def by_technology(self, request):
        """Analyse par technologie"""
        technology = request.query_params.get('tech')
        if not technology:
            return Response({"error": "Paramètre 'tech' requis"}, status=400)
        
        jobs = Job.objects.filter(
            technologies__icontains=technology
        ).values('country').annotate(
            count=Count('id'),
            avg_salary=Avg('salary_avg')
        ).order_by('-count')
        
        return Response({
            'technology': technology,
            'total_jobs': sum(job['count'] for job in jobs),
            'by_country': list(jobs)
        })


class GitHubRepoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les repositories GitHub"""
    queryset = GitHubRepo.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['language']
    search_fields = ['repo_name', 'description']
    ordering_fields = ['stars', 'forks', 'created_at']
    ordering = ['-stars']

    def get_serializer_class(self):
        if self.action == 'list':
            return GitHubRepoListSerializer
        return GitHubRepoDetailSerializer

    @action(detail=False, methods=['get'])
    def top_languages(self, request):
        """Top des langages de programmation"""
        languages = GitHubRepo.objects.values('language').annotate(
            count=Count('repo_id'),
            total_stars=Sum('stars'),
            avg_stars=Avg('stars')
        ).order_by('-total_stars').exclude(language__isnull=True)
        return Response(languages)


class GoogleTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les tendances Google"""
    queryset = GoogleTrend.objects.all()
    serializer_class = GoogleTrendSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['keyword', 'country']
    ordering_fields = ['date', 'interest_score']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def trending_now(self, request):
        """Technologies tendances actuellement"""
        recent_trends = GoogleTrend.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        ).values('keyword').annotate(
            avg_interest=Avg('interest_score'),
            max_interest=Max('interest_score')
        ).order_by('-avg_interest')[:10]
        return Response(recent_trends)

    @action(detail=False, methods=['get'])
    def top_technologies(self, request):
        """Top 5 des technologies les plus utilisées dans Google Trends"""
        top_keywords = GoogleTrend.objects.values('keyword').annotate(
            total_interest=Sum('interest_score'),
            avg_interest=Avg('interest_score'),
            count_entries=Count('id')
        ).order_by('-total_interest')[:5]
        
        return Response({
            'message': 'Top 5 des technologies les plus utilisées',
            'data': list(top_keywords)
        })


class DeveloperViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les développeurs"""
    queryset = Developer.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'employment', 'remote_work']
    search_fields = ['job_title', 'technologies']
    ordering_fields = ['salary']
    ordering = ['-salary']

    def get_serializer_class(self):
        if self.action == 'list':
            return DeveloperListSerializer
        return DeveloperDetailSerializer

    @action(detail=False, methods=['get'])
    def salary_by_experience(self, request):
        """Salaires par niveau d'expérience"""
        experience_levels = ['junior', 'mid', 'senior', 'expert']
        results = []
        
        for level in experience_levels:
            if level == 'junior':
                queryset = Developer.objects.filter(years_coding_pro__in=['0', '1', '2'])
            elif level == 'mid':
                queryset = Developer.objects.filter(years_coding_pro__in=['3', '4', '5'])
            elif level == 'senior':
                queryset = Developer.objects.filter(years_coding_pro__in=['6', '7', '8', '9', '10'])
            else:  # expert
                queryset = Developer.objects.exclude(years_coding_pro__in=[
                    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
                ])
            
            stats = queryset.aggregate(
                count=Count('respondent_id'),
                avg_salary=Avg('salary'),
                min_salary=Min('salary'),
                max_salary=Max('salary')
            )
            stats['experience_level'] = level
            results.append(stats)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def average_salary_by_employment(self, request):
        """Salaire moyen par type d'employment"""
        employment_type = request.query_params.get('employment')
        
        if not employment_type:
            # Retourner tous les types d'employment avec leurs salaires moyens
            employment_stats = Developer.objects.exclude(
                salary__isnull=True
            ).values('employment').annotate(
                avg_salary=Avg('salary'),
                count=Count('respondent_id'),
                min_salary=Min('salary'),
                max_salary=Max('salary')
            ).order_by('-avg_salary')
            
            return Response({
                'message': 'Salaire moyen par type d\'employment',
                'data': list(employment_stats)
            })
        else:
            # Retourner le salaire moyen pour un employment spécifique
            stats = Developer.objects.filter(
                employment=employment_type,
                salary__isnull=False
            ).aggregate(
                avg_salary=Avg('salary'),
                count=Count('respondent_id'),
                min_salary=Min('salary'),
                max_salary=Max('salary')
            )
            
            if stats['count'] == 0:
                return Response({
                    'message': f'Aucun développeur trouvé pour l\'employment: {employment_type}',
                    'employment': employment_type,
                    'data': None
                }, status=404)
            
            return Response({
                'message': f'Salaire moyen pour employment: {employment_type}',
                'employment': employment_type,
                'data': stats
            })

    @action(detail=False, methods=['get'])
    def top_freelancer_job_titles(self, request):
        """Job titles avec le plus de freelancers"""
        freelancer_jobs = Developer.objects.filter(
            employment='Freelancer'
        ).values('job_title').annotate(
            freelancer_count=Count('respondent_id'),
            avg_salary=Avg('salary')
        ).order_by('-freelancer_count')[:10]
        
        return Response({
            'message': 'Job titles avec le plus de freelancers',
            'data': list(freelancer_jobs)
        })

    @action(detail=False, methods=['get'])
    def highest_paid_job_titles(self, request):
        """Job titles les mieux payés"""
        highest_paid = Developer.objects.exclude(
            salary__isnull=True
        ).values('job_title').annotate(
            avg_salary=Avg('salary'),
            max_salary=Max('salary'),
            count=Count('respondent_id')
        ).order_by('-avg_salary')[:10]
        
        return Response({
            'message': 'Job titles les mieux payés',
            'data': list(highest_paid)
        })


class KaggleDatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les datasets Kaggle"""
    queryset = KaggleDataset.objects.all()
    serializer_class = KaggleDatasetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location']
    search_fields = ['job_title', 'technologies']
    ordering_fields = ['salary', 'experience_years']
    ordering = ['-salary']

    @action(detail=False, methods=['get'])
    def best_paid_technology(self, request):
        """Technologie la mieux payée dans Kaggle"""
        # Analyser les technologies dans le champ technologies
        tech_salaries = {}
        
        # Récupérer tous les datasets avec salaire et technologies
        datasets = KaggleDataset.objects.exclude(
            salary__isnull=True
        ).exclude(
            technologies__isnull=True
        ).exclude(
            technologies__exact=''
        )
        
        for dataset in datasets:
            if dataset.technologies:
                # Séparer les technologies (par virgule généralement)
                techs = [tech.strip().lower() for tech in dataset.technologies.split(',')]
                for tech in techs:
                    if tech and len(tech) > 1:  # Éviter les chaînes vides ou trop courtes
                        if tech not in tech_salaries:
                            tech_salaries[tech] = []
                        tech_salaries[tech].append(float(dataset.salary))
        
        # Calculer les moyennes et compter les occurrences
        tech_stats = []
        for tech, salaries in tech_salaries.items():
            if len(salaries) >= 2:  # Au moins 2 occurrences pour être significatif
                tech_stats.append({
                    'technology': tech,
                    'avg_salary': sum(salaries) / len(salaries),
                    'max_salary': max(salaries),
                    'min_salary': min(salaries),
                    'count': len(salaries)
                })
        
        # Trier par salaire moyen décroissant
        tech_stats.sort(key=lambda x: x['avg_salary'], reverse=True)
        
        return Response({
            'message': 'Technologies les mieux payées (Kaggle)',
            'data': tech_stats[:10]  # Top 10
        })

    @action(detail=False, methods=['get'])
    def junior_average_salary(self, request):
        """Salaire moyen des juniors (Kaggle)"""
        # Considérer comme junior : experience_years <= 2 ou null
        junior_datasets = KaggleDataset.objects.filter(
            Q(experience_years__lte=2) | Q(experience_years__isnull=True),
            salary__isnull=False
        )
        
        stats = junior_datasets.aggregate(
            avg_salary=Avg('salary'),
            min_salary=Min('salary'),
            max_salary=Max('salary'),
            count=Count('id')
        )
        
        # Détails par années d'expérience
        experience_breakdown = junior_datasets.values('experience_years').annotate(
            avg_salary=Avg('salary'),
            count=Count('id')
        ).order_by('experience_years')
        
        return Response({
            'message': 'Salaire moyen des juniors (≤2 ans d\'expérience)',
            'global_stats': stats,
            'by_experience_years': list(experience_breakdown)
        })


class JobsConsolidatedViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour la vue consolidée des emplois"""
    queryset = JobsConsolidated.objects.all()
    serializer_class = JobsConsolidatedSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'source']
    search_fields = ['title', 'company', 'technologies']
    ordering = ['-loaded_at']


# =================
# VUES D'ANALYSE ET STATISTIQUES
# =================

class StatisticsView(views.APIView):
    """Vue pour les statistiques globales"""

    def get(self, request):
        stats = {
            'total_jobs': Job.objects.count(),
            'total_github_repos': GitHubRepo.objects.count(),
            'total_trends': GoogleTrend.objects.count(),
            'total_developers': Developer.objects.count(),
            'total_kaggle_datasets': KaggleDataset.objects.count(),
            'total_companies': DCompany.objects.count(),
            'total_skills': DSkill.objects.count(),
            'total_countries': DCountry.objects.count(),
            'total_sources': DSource.objects.count(),
            'last_update': timezone.now()
        }
        return Response(stats)


class SalaryAnalysisView(views.APIView):
    """Vue pour l'analyse des salaires"""

    def get(self, request):
        country = request.query_params.get('country')
        technology = request.query_params.get('technology')
        
        # Analyse des emplois
        jobs_query = Job.objects.exclude(salary_avg__isnull=True)
        if country:
            jobs_query = jobs_query.filter(country=country)
        if technology:
            jobs_query = jobs_query.filter(technologies__icontains=technology)
        
        jobs_stats = jobs_query.aggregate(
            count=Count('id'),
            avg_salary=Avg('salary_avg'),
            min_salary=Min('salary_avg'),
            max_salary=Max('salary_avg')
        )
        
        # Analyse des développeurs
        dev_query = Developer.objects.exclude(salary__isnull=True)
        if country:
            dev_query = dev_query.filter(country=country)
        if technology:
            dev_query = dev_query.filter(technologies__icontains=technology)
        
        dev_stats = dev_query.aggregate(
            count=Count('respondent_id'),
            avg_salary=Avg('salary'),
            min_salary=Min('salary'),
            max_salary=Max('salary')
        )
        
        # Analyse Kaggle
        kaggle_query = KaggleDataset.objects.exclude(salary__isnull=True)
        if technology:
            kaggle_query = kaggle_query.filter(technologies__icontains=technology)
        
        kaggle_stats = kaggle_query.aggregate(
            count=Count('id'),
            avg_salary=Avg('salary'),
            min_salary=Min('salary'),
            max_salary=Max('salary')
        )
        
        return Response({
            'filters': {'country': country, 'technology': technology},
            'jobs_data': jobs_stats,
            'developers_data': dev_stats,
            'kaggle_data': kaggle_stats
        })


class TechnologyTrendsView(views.APIView):
    """Vue pour l'analyse des tendances technologiques"""

    def get(self, request):
        technology = request.query_params.get('tech')
        if not technology:
            return Response({"error": "Paramètre 'tech' requis"}, status=400)
        
        # Données des emplois
        job_count = Job.objects.filter(technologies__icontains=technology).count()
        avg_job_salary = Job.objects.filter(
            technologies__icontains=technology,
            salary_avg__isnull=False
        ).aggregate(avg_salary=Avg('salary_avg'))['avg_salary']
        
        # Données GitHub
        github_repos = GitHubRepo.objects.filter(
            Q(repo_name__icontains=technology) | Q(description__icontains=technology)
        ).count()
        
        # Tendances Google
        recent_trends = GoogleTrend.objects.filter(
            keyword__icontains=technology,
            date__gte=timezone.now().date() - timedelta(days=90)
        ).aggregate(avg_interest=Avg('interest_score'))['avg_interest']
        
        # Développeurs
        dev_count = Developer.objects.filter(technologies__icontains=technology).count()
        avg_dev_salary = Developer.objects.filter(
            technologies__icontains=technology,
            salary__isnull=False
        ).aggregate(avg_salary=Avg('salary'))['avg_salary']
        
        return Response({
            'technology': technology,
            'job_count': job_count,
            'avg_job_salary': avg_job_salary,
            'github_repos': github_repos,
            'avg_trend_score': recent_trends,
            'developer_count': dev_count,
            'avg_developer_salary': avg_dev_salary
        })


class CountryAnalysisView(views.APIView):
    """Vue pour l'analyse par pays"""

    def get(self, request):
        country = request.query_params.get('country')
        if not country:
            return Response({"error": "Paramètre 'country' requis"}, status=400)
        
        # Informations du pays
        try:
            country_info = DCountry.objects.get(iso2=country.upper())
            country_data = DCountrySerializer(country_info).data
        except DCountry.DoesNotExist:
            country_data = {'iso2': country, 'country_name': 'Inconnu'}
        
        # Statistiques des emplois
        jobs = Job.objects.filter(country=country.upper())
        job_stats = jobs.aggregate(
            count=Count('id'),
            avg_salary=Avg('salary_avg')
        )
        
        # Top technologies dans ce pays
        tech_analysis = defaultdict(int)
        for job in jobs:
            if job.technologies:
                techs = [t.strip().lower() for t in job.technologies.split(',')]
                for tech in techs:
                    if tech:
                        tech_analysis[tech] += 1
        
        top_technologies = sorted(tech_analysis.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Développeurs
        dev_stats = Developer.objects.filter(country=country.upper()).aggregate(
            count=Count('respondent_id'),
            avg_salary=Avg('salary')
        )
        
        return Response({
            'country_info': country_data,
            'job_statistics': job_stats,
            'developer_statistics': dev_stats,
            'top_technologies': [{'tech': tech, 'count': count} for tech, count in top_technologies]
        })


class RemoteWorkAnalysisView(views.APIView):
    """Vue pour l'analyse du travail à distance"""

    def get(self, request):
        # Jobs avec politique remote
        remote_jobs = Job.objects.filter(contract_type__icontains='remote').count()
        total_jobs = Job.objects.count()
        
        # Développeurs remote
        remote_devs = Developer.objects.values('remote_work').annotate(
            count=Count('respondent_id'),
            avg_salary=Avg('salary')
        ).order_by('-count')
        
        # Pays avec le plus d'opportunités remote
        remote_by_country = Job.objects.filter(
            contract_type__icontains='remote'
        ).values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'remote_job_percentage': (remote_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            'remote_policies': list(remote_devs),
            'top_remote_countries': list(remote_by_country)
        })


# =================
# ENDPOINTS UTILITAIRES
# =================

@api_view(['GET'])
def health_check(request):
    """Endpoint de vérification de l'état de l'API"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'database': 'connected'
    })


@api_view(['GET'])
def data_freshness(request):
    """Vérification de la fraîcheur des données"""
    latest_job = Job.objects.order_by('-loaded_at').first()
    latest_github = GitHubRepo.objects.order_by('-loaded_at').first()
    latest_trend = GoogleTrend.objects.order_by('-loaded_at').first()
    latest_dev = Developer.objects.order_by('-loaded_at').first()
    
    return Response({
        'last_job_update': latest_job.loaded_at if latest_job else None,
        'last_github_update': latest_github.loaded_at if latest_github else None,
        'last_trend_update': latest_trend.loaded_at if latest_trend else None,
        'last_developer_update': latest_dev.loaded_at if latest_dev else None
    }) 