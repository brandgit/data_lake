"""
Models for JobTech API - Correspondance avec les tables du Data Warehouse PostgreSQL
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# =================
# TABLES DE DIMENSIONS
# =================

class DDate(models.Model):
    """Table de dimension des dates"""
    date_key = models.DateField(primary_key=True)
    day = models.SmallIntegerField()
    month = models.SmallIntegerField()
    quarter = models.SmallIntegerField()
    year = models.SmallIntegerField()
    day_week = models.SmallIntegerField()

    class Meta:
        managed = False  # Django ne gère pas cette table
        db_table = 'd_date'
        ordering = ['date_key']

    def __str__(self):
        return str(self.date_key)


class DCountry(models.Model):
    """Table de dimension des pays"""
    id_country = models.AutoField(primary_key=True)
    iso2 = models.CharField(max_length=2, unique=True)
    country_name = models.TextField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    monnaie_iso3 = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_country'
        ordering = ['country_name']

    def __str__(self):
        return f"{self.country_name} ({self.iso2})"


class DCompany(models.Model):
    """Table de dimension des entreprises"""
    id_company = models.BigAutoField(primary_key=True)
    company_name = models.TextField(blank=True, null=True)
    workforce_size = models.TextField(blank=True, null=True)
    sector = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_company'
        ordering = ['company_name']

    def __str__(self):
        return self.company_name or f"Company {self.id_company}"


class DSkill(models.Model):
    """Table de dimension des compétences"""
    id_skill = models.AutoField(primary_key=True)
    skill_group = models.TextField(blank=True, null=True)
    tech_label = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_skill'
        ordering = ['tech_label']

    def __str__(self):
        return f"{self.tech_label} ({self.skill_group})"


class DSource(models.Model):
    """Table de dimension des sources de données"""
    id_source = models.SmallAutoField(primary_key=True)
    source_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_source'
        ordering = ['source_name']

    def __str__(self):
        return self.source_name or f"Source {self.id_source}"


# =================
# TABLES DE FAITS
# =================

class Job(models.Model):
    """Table des offres d'emploi (Adzuna + RemoteOK)"""
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=300, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    country = models.CharField(max_length=10, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_avg = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    contract_type = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=50)
    extracted_at = models.DateTimeField(blank=True, null=True)
    cleaned_at = models.DateTimeField(blank=True, null=True)
    loaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'jobs'
        ordering = ['-loaded_at']

    def __str__(self):
        return f"{self.title} - {self.company}"

    @property
    def technologies_list(self):
        """Retourne les technologies sous forme de liste"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
        return []


class GitHubRepo(models.Model):
    """Table des repositories GitHub"""
    repo_id = models.BigIntegerField(primary_key=True)
    repo_name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    created_at = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=50, default='github')
    cleaned_at = models.DateTimeField(blank=True, null=True)
    loaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'github_repos'
        ordering = ['-stars']

    def __str__(self):
        return self.repo_name

    @property
    def popularity_category(self):
        """Catégorise la popularité du repository"""
        if self.stars >= 1000:
            return 'high'
        elif self.stars >= 100:
            return 'medium'
        else:
            return 'low'


class GoogleTrend(models.Model):
    """Table des tendances Google Trends"""
    id = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=200)
    date = models.DateField()
    interest_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    country = models.CharField(max_length=10, blank=True, null=True)
    source = models.CharField(max_length=50, default='google_trends')
    cleaned_at = models.DateTimeField(blank=True, null=True)
    loaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'google_trends'
        ordering = ['-date']
        unique_together = ['keyword', 'date', 'country']

    def __str__(self):
        return f"{self.keyword} - {self.date}"


class Developer(models.Model):
    """Table des développeurs StackOverflow"""
    respondent_id = models.IntegerField(primary_key=True)
    job_title = models.CharField(max_length=300, blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    years_coding_pro = models.CharField(max_length=50, blank=True, null=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    employment = models.CharField(max_length=100, blank=True, null=True)
    org_size = models.CharField(max_length=100, blank=True, null=True)
    remote_work = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=50, default='stackoverflow')
    cleaned_at = models.DateTimeField(blank=True, null=True)
    loaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'developers'
        ordering = ['-salary']

    def __str__(self):
        return f"{self.job_title} - {self.country}"

    @property
    def technologies_list(self):
        """Retourne les technologies sous forme de liste"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
        return []

    @property
    def experience_level(self):
        """Détermine le niveau d'expérience"""
        if not self.years_coding_pro:
            return 'unknown'
        try:
            years = int(self.years_coding_pro)
            if years <= 2:
                return 'junior'
            elif years <= 5:
                return 'mid'
            elif years <= 10:
                return 'senior'
            else:
                return 'expert'
        except (ValueError, TypeError):
            return 'unknown'


class KaggleDataset(models.Model):
    """Table des datasets Kaggle"""
    id = models.IntegerField(primary_key=True)
    job_title = models.CharField(max_length=300, blank=True, null=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    dataset_source = models.CharField(max_length=500, blank=True, null=True)
    source = models.CharField(max_length=50, default='kaggle')
    cleaned_at = models.DateTimeField(blank=True, null=True)
    loaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'kaggle_datasets'
        ordering = ['-salary']

    def __str__(self):
        return f"{self.job_title} - {self.location}"

    @property
    def technologies_list(self):
        """Retourne les technologies sous forme de liste"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
        return []

    @property
    def experience_level(self):
        """Détermine le niveau d'expérience"""
        if not self.experience_years:
            return 'unknown'
        if self.experience_years <= 2:
            return 'junior'
        elif self.experience_years <= 5:
            return 'mid'
        elif self.experience_years <= 10:
            return 'senior'
        else:
            return 'expert'


# =================
# VUES AGGREGÉES
# =================

class JobsConsolidated(models.Model):
    """Vue consolidée des emplois"""
    unified_id = models.CharField(max_length=100, primary_key=True)
    source_id = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=300, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    country = models.CharField(max_length=10, blank=True, null=True)
    estimated_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=50)
    loaded_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'v_jobs_consolidated'
        ordering = ['-loaded_at']

    def __str__(self):
        return f"{self.title} - {self.company}" 