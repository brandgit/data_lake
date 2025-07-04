"""
Extract utilities for JobTech project
Contains all data extraction classes and utilities
"""

from .api_extractors import (
    AdzunaExtractor,
    GitHubExtractor, 
    RemoteOKExtractor,
    KaggleExtractor
)

from .scraping_extractors import (
    StackOverflowExtractor,
    GoogleTrendsExtractor,
    IndeedRSSExtractor
)

from .base_extractors import (
    BaseAPIExtractor,
    BaseScrapeExtractor,
    Config
)

__all__ = [
    # Base classes
    'BaseAPIExtractor',
    'BaseScrapeExtractor', 
    'Config',
    
    # API extractors
    'AdzunaExtractor',
    'GitHubExtractor',
    'RemoteOKExtractor', 
    'KaggleExtractor',
    
    # Scraping extractors
    'StackOverflowExtractor',
    'GoogleTrendsExtractor',
    'IndeedRSSExtractor'
] 