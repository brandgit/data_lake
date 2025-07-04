"""
Serializers for JobTech API - Data Warehouse PostgreSQL
"""

from rest_framework import serializers
from .models import (
    # Tables de dimensions
    DDate, DCountry, DCompany, DSkill, DSource,
    # Tables de faits
    Job, GitHubRepo, GoogleTrend, Developer, KaggleDataset,
    # Vues
    JobsConsolidated
)


# =================
# SERIALIZERS DES DIMENSIONS
# =================

class DDateSerializer(serializers.ModelSerializer):
    """Serializer pour la dimension dates"""
    
    class Meta:
        model = DDate
        fields = ['date_key', 'day', 'month', 'quarter', 'year', 'day_week']


class DCountrySerializer(serializers.ModelSerializer):
    """Serializer pour la dimension pays"""
    
    class Meta:
        model = DCountry
        fields = ['id_country', 'iso2', 'country_name', 'region', 'monnaie_iso3']


class DCompanySerializer(serializers.ModelSerializer):
    """Serializer pour la dimension entreprises"""
    
    class Meta:
        model = DCompany
        fields = ['id_company', 'company_name', 'workforce_size', 'sector']


class DSkillSerializer(serializers.ModelSerializer):
    """Serializer pour la dimension compétences"""
    
    class Meta:
        model = DSkill
        fields = ['id_skill', 'skill_group', 'tech_label']


class DSourceSerializer(serializers.ModelSerializer):
    """Serializer pour la dimension sources"""
    
    class Meta:
        model = DSource
        fields = ['id_source', 'source_name']


# =================
# SERIALIZERS DES TABLES DE FAITS
# =================

class JobListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des emplois"""
    technologies_list = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location', 'country',
            'salary_min', 'salary_max', 'salary_avg',
            'contract_type', 'source', 'technologies_list',
            'extracted_at', 'loaded_at'
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un emploi"""
    technologies_list = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location', 'country',
            'salary_min', 'salary_max', 'salary_avg', 'salary',
            'description', 'technologies', 'technologies_list',
            'contract_type', 'source', 'extracted_at',
            'cleaned_at', 'loaded_at'
        ]


class GitHubRepoListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des repos GitHub"""
    popularity_category = serializers.ReadOnlyField()
    
    class Meta:
        model = GitHubRepo
        fields = [
            'repo_id', 'repo_name', 'language', 'stars',
            'forks', 'popularity_category', 'created_at'
        ]


class GitHubRepoDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un repo GitHub"""
    popularity_category = serializers.ReadOnlyField()
    
    class Meta:
        model = GitHubRepo
        fields = [
            'repo_id', 'repo_name', 'description', 'language',
            'stars', 'forks', 'popularity_category', 'source',
            'created_at', 'cleaned_at', 'loaded_at'
        ]


class GoogleTrendSerializer(serializers.ModelSerializer):
    """Serializer pour les tendances Google"""
    
    class Meta:
        model = GoogleTrend
        fields = [
            'id', 'keyword', 'date', 'interest_score',
            'country', 'source', 'cleaned_at', 'loaded_at'
        ]


class DeveloperListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des développeurs"""
    experience_level = serializers.ReadOnlyField()
    
    class Meta:
        model = Developer
        fields = [
            'respondent_id', 'job_title', 'years_coding_pro',
            'salary', 'employment', 'remote_work',
            'country', 'experience_level'
        ]


class DeveloperDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un développeur"""
    technologies_list = serializers.ReadOnlyField()
    experience_level = serializers.ReadOnlyField()
    
    class Meta:
        model = Developer
        fields = [
            'respondent_id', 'job_title', 'technologies',
            'technologies_list', 'years_coding_pro', 'salary',
            'employment', 'org_size', 'remote_work', 'country',
            'experience_level', 'source', 'cleaned_at', 'loaded_at'
        ]


class KaggleDatasetSerializer(serializers.ModelSerializer):
    """Serializer pour les datasets Kaggle"""
    technologies_list = serializers.ReadOnlyField()
    experience_level = serializers.ReadOnlyField()
    
    class Meta:
        model = KaggleDataset
        fields = [
            'id', 'job_title', 'salary', 'experience_years',
            'location', 'technologies', 'technologies_list',
            'experience_level', 'dataset_source', 'source',
            'cleaned_at', 'loaded_at'
        ]


class JobsConsolidatedSerializer(serializers.ModelSerializer):
    """Serializer pour la vue consolidée des emplois"""
    
    class Meta:
        model = JobsConsolidated
        fields = [
            'unified_id', 'source_id', 'title', 'company',
            'location', 'country', 'estimated_salary',
            'technologies', 'source', 'loaded_at'
        ]


# =================
# SERIALIZERS POUR LES STATISTIQUES
# =================

class StatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques globales"""
    total_jobs = serializers.IntegerField()
    total_github_repos = serializers.IntegerField()
    total_trends = serializers.IntegerField()
    total_developers = serializers.IntegerField()
    total_kaggle_datasets = serializers.IntegerField()
    total_companies = serializers.IntegerField()
    total_skills = serializers.IntegerField()
    total_countries = serializers.IntegerField()
    total_sources = serializers.IntegerField()
    last_update = serializers.DateTimeField()


class SalaryStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques salariales"""
    country = serializers.CharField()
    job_title = serializers.CharField()
    source = serializers.CharField()
    avg_salary = serializers.FloatField()
    min_salary = serializers.FloatField()
    max_salary = serializers.FloatField()
    count = serializers.IntegerField()


class TechnologyStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des technologies"""
    technology = serializers.CharField()
    job_count = serializers.IntegerField()
    avg_salary = serializers.FloatField()
    github_repos = serializers.IntegerField()
    trend_score = serializers.FloatField()


class CountryStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques par pays"""
    country = serializers.CharField()
    country_name = serializers.CharField()
    job_count = serializers.IntegerField()
    avg_salary = serializers.FloatField()
    top_technologies = serializers.ListField(child=serializers.CharField())


class TrendAnalysisSerializer(serializers.Serializer):
    """Serializer pour l'analyse des tendances"""
    keyword = serializers.CharField()
    current_interest = serializers.FloatField()
    trend_direction = serializers.CharField()  # 'up', 'down', 'stable'
    monthly_change = serializers.FloatField()
    countries = serializers.ListField(child=serializers.CharField())


class ExperienceStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques par niveau d'expérience"""
    experience_level = serializers.CharField()
    count = serializers.IntegerField()
    avg_salary = serializers.FloatField()
    popular_technologies = serializers.ListField(child=serializers.CharField())
    remote_percentage = serializers.FloatField()


class CompanyStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des entreprises"""
    company_name = serializers.CharField()
    job_count = serializers.IntegerField()
    avg_salary = serializers.FloatField()
    technologies = serializers.ListField(child=serializers.CharField())
    locations = serializers.ListField(child=serializers.CharField())


class SkillDemandSerializer(serializers.Serializer):
    """Serializer pour la demande de compétences"""
    skill_group = serializers.CharField()
    tech_label = serializers.CharField()
    job_mentions = serializers.IntegerField()
    github_projects = serializers.IntegerField()
    salary_impact = serializers.FloatField()
    trend_score = serializers.FloatField()


class RemoteWorkStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques du travail à distance"""
    remote_policy = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()
    avg_salary = serializers.FloatField()
    top_countries = serializers.ListField(child=serializers.CharField()) 