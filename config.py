"""
Configuration pour le projet JobTech
"""

class Config:
    """Configuration de la base de données PostgreSQL"""
    
    # Configuration PostgreSQL (conteneur Docker)
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'jobtech_db'
    DB_USER = 'jobtech_user'
    DB_PASSWORD = 'jobtech_pass'
    
    # Configuration des répertoires
    RAW_DATA_DIR = 'raw'
    CLEAN_DATA_DIR = 'datasets_clean'
    
    # Configuration des logs
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'data_pipeline.log' 