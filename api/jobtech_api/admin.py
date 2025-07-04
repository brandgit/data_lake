"""
Admin configuration for JobTech API - Data Warehouse PostgreSQL
"""

from django.contrib import admin
from .models import (
    # Tables de dimensions
    DDate, DCountry, DCompany, DSkill, DSource,
    # Tables de faits
    Job, GitHubRepo, GoogleTrend, Developer, KaggleDataset,
    # Vues
    JobsConsolidated
)


# =================
# ADMIN DES DIMENSIONS
# =================

@admin.register(DCountry)
class DCountryAdmin(admin.ModelAdmin):
    """Admin pour les pays"""
    list_display = ['iso2', 'country_name', 'region', 'monnaie_iso3']
    list_filter = ['region']
    search_fields = ['country_name', 'iso2']
    ordering = ['country_name']


@admin.register(DCompany)
class DCompanyAdmin(admin.ModelAdmin):
    """Admin pour les entreprises"""
    list_display = ['company_name', 'workforce_size', 'sector']
    list_filter = ['workforce_size', 'sector']
    search_fields = ['company_name']
    ordering = ['company_name']


@admin.register(DSkill)
class DSkillAdmin(admin.ModelAdmin):
    """Admin pour les compétences"""
    list_display = ['tech_label', 'skill_group']
    list_filter = ['skill_group']
    search_fields = ['tech_label']
    ordering = ['tech_label']


@admin.register(DSource)
class DSourceAdmin(admin.ModelAdmin):
    """Admin pour les sources"""
    list_display = ['source_name']
    search_fields = ['source_name']
    ordering = ['source_name']


# =================
# ADMIN DES TABLES DE FAITS
# =================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin pour les emplois"""
    list_display = ['title', 'company', 'country', 'salary_avg', 'source', 'loaded_at']
    list_filter = ['country', 'source', 'contract_type']
    search_fields = ['title', 'company', 'technologies']
    ordering = ['-loaded_at']
    readonly_fields = ['loaded_at', 'cleaned_at']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('id', 'title', 'company', 'location', 'country')
        }),
        ('Salaire', {
            'fields': ('salary_min', 'salary_max', 'salary_avg', 'salary')
        }),
        ('Détails', {
            'fields': ('description', 'technologies', 'contract_type')
        }),
        ('Métadonnées', {
            'fields': ('source', 'extracted_at', 'cleaned_at', 'loaded_at')
        }),
    )


@admin.register(GitHubRepo)
class GitHubRepoAdmin(admin.ModelAdmin):
    """Admin pour les repositories GitHub"""
    list_display = ['repo_name', 'language', 'stars', 'forks', 'popularity_category']
    list_filter = ['language']
    search_fields = ['repo_name', 'description']
    ordering = ['-stars']
    readonly_fields = ['loaded_at', 'cleaned_at', 'popularity_category']

    def popularity_category(self, obj):
        return obj.popularity_category
    popularity_category.short_description = 'Popularité'


@admin.register(GoogleTrend)
class GoogleTrendAdmin(admin.ModelAdmin):
    """Admin pour les tendances Google"""
    list_display = ['keyword', 'date', 'interest_score', 'country']
    list_filter = ['country', 'date']
    search_fields = ['keyword']
    ordering = ['-date', '-interest_score']
    readonly_fields = ['loaded_at', 'cleaned_at']


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    """Admin pour les développeurs"""
    list_display = ['job_title', 'country', 'salary', 'experience_level', 'remote_work']
    list_filter = ['country', 'employment', 'remote_work']
    search_fields = ['job_title', 'technologies']
    ordering = ['-salary']
    readonly_fields = ['loaded_at', 'cleaned_at', 'experience_level']

    def experience_level(self, obj):
        return obj.experience_level
    experience_level.short_description = 'Niveau'


@admin.register(KaggleDataset)
class KaggleDatasetAdmin(admin.ModelAdmin):
    """Admin pour les datasets Kaggle"""
    list_display = ['job_title', 'location', 'salary', 'experience_level']
    list_filter = ['location']
    search_fields = ['job_title', 'technologies']
    ordering = ['-salary']
    readonly_fields = ['loaded_at', 'cleaned_at', 'experience_level']

    def experience_level(self, obj):
        return obj.experience_level
    experience_level.short_description = 'Niveau'


@admin.register(JobsConsolidated)
class JobsConsolidatedAdmin(admin.ModelAdmin):
    """Admin pour la vue consolidée des emplois"""
    list_display = ['title', 'company', 'country', 'estimated_salary', 'source']
    list_filter = ['country', 'source']
    search_fields = ['title', 'company', 'technologies']
    ordering = ['-loaded_at']

    def has_add_permission(self, request):
        # Vue en lecture seule
        return False

    def has_change_permission(self, request, obj=None):
        # Vue en lecture seule
        return False

    def has_delete_permission(self, request, obj=None):
        # Vue en lecture seule
        return False


# Configuration globale de l'admin
admin.site.site_header = "JobTech Data Warehouse Admin"
admin.site.site_title = "JobTech DWH"
admin.site.index_title = "Administration du Data Warehouse JobTech" 