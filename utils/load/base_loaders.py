"""
Classes de base pour le chargement de données vers PostgreSQL
"""

import os
import sys
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Configuration de la base de données PostgreSQL"""
    host: str = 'localhost'
    port: int = 5432
    database: str = 'jobtech_dwh'
    user: str = 'postgres'
    password: str = 'password'
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Crée une configuration depuis les variables d'environnement"""
        return cls(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB', 'jobtech_dwh'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
    
    @classmethod
    def from_config_file(cls, config_path: Path) -> 'DatabaseConfig':
        """Charge la configuration depuis un fichier config.py"""
        try:
            sys.path.insert(0, str(config_path.parent))
            from config import Config
            cfg = Config()
            return cls(
                host=cfg.DB_HOST,
                port=int(cfg.DB_PORT),
                database=cfg.DB_NAME,
                user=cfg.DB_USER,
                password=cfg.DB_PASSWORD
            )
        except Exception as e:
            logger.warning(f"Impossible de charger {config_path}: {e}")
            return cls.from_env()
    
    def get_connection_string(self) -> str:
        """Retourne la chaîne de connexion PostgreSQL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class LoadingStats:
    """Statistiques de chargement de données"""
    table_name: str
    total_rows: int = 0
    inserted_rows: int = 0
    updated_rows: int = 0
    skipped_rows: int = 0
    error_rows: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def start(self):
        """Démarre le chronomètre"""
        self.start_time = datetime.now()
    
    def end(self):
        """Arrête le chronomètre"""
        self.end_time = datetime.now()
    
    @property
    def duration(self) -> Optional[float]:
        """Durée en secondes"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Taux de succès en pourcentage"""
        if self.total_rows == 0:
            return 0.0
        return (self.inserted_rows + self.updated_rows) / self.total_rows * 100
    
    def __str__(self) -> str:
        """Représentation textuelle des statistiques"""
        duration_str = f"{self.duration:.2f}s" if self.duration else "N/A"
        return (f"Table {self.table_name}: {self.inserted_rows}/{self.total_rows} "
                f"insertions ({self.success_rate:.1f}%) en {duration_str}")


class BaseLoader:
    """Classe de base pour tous les chargeurs de données"""
    
    def __init__(self, config: DatabaseConfig = None):
        """Initialise le chargeur avec la configuration de base de données"""
        self.config = config or DatabaseConfig.from_env()
        self.engine = None
        self.project_root = Path(__file__).parent.parent.parent
        self.datasets_dir = self.project_root / "datasets_clean"
        self.stats: List[LoadingStats] = []
        
    def connect(self) -> bool:
        """Établit la connexion à PostgreSQL"""
        try:
            self.engine = create_engine(self.config.get_connection_string())
            # Test de connexion
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Connexion PostgreSQL établie: {self.config.host}:{self.config.port}/{self.config.database}")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion PostgreSQL: {e}")
            return False
    
    def execute_sql(self, sql: str) -> bool:
        """Exécute une requête SQL"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erreur SQL: {e}")
            return False
    
    def execute_sql_file(self, sql_file_path: Path) -> bool:
        """Exécute un fichier SQL"""
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            return self.execute_sql(sql_content)
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du fichier SQL {sql_file_path}: {e}")
            return False
    
    def load_dataframe(self, df: pd.DataFrame, table_name: str, 
                      if_exists: str = 'append', chunksize: int = 1000) -> LoadingStats:
        """Charge un DataFrame dans une table PostgreSQL"""
        stats = LoadingStats(table_name=table_name, total_rows=len(df))
        stats.start()
        
        try:
            # Nettoyage des données
            df_clean = df.copy()
            df_clean = df_clean.fillna('')  # Remplacer NaN par chaîne vide
            
            # Chargement par chunks
            df_clean.to_sql(table_name, self.engine, if_exists=if_exists, 
                           index=False, chunksize=chunksize)
            
            stats.inserted_rows = len(df_clean)
            logger.info(f"{table_name}: {stats.inserted_rows} lignes chargées")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {table_name}: {e}")
            stats.error_rows = len(df)
        
        stats.end()
        self.stats.append(stats)
        return stats
    
    def load_csv_file(self, csv_file: Path, table_name: str, 
                     column_mapping: Dict[str, str] = None,
                     if_exists: str = 'append') -> LoadingStats:
        """Charge un fichier CSV dans une table"""
        try:
            df = pd.read_csv(csv_file)
            
            # Appliquer le mapping des colonnes si fourni
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            return self.load_dataframe(df, table_name, if_exists)
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier {csv_file}: {e}")
            stats = LoadingStats(table_name=table_name)
            stats.error_rows = 1
            return stats
    
    def get_table_count(self, table_name: str) -> int:
        """Retourne le nombre de lignes dans une table"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
        except Exception as e:
            logger.error(f"Erreur lors du comptage de la table {table_name}: {e}")
            return 0
    
    def table_exists(self, table_name: str) -> bool:
        """Vérifie si une table existe"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = :table_name
                    )
                """), {"table_name": table_name})
                return result.scalar()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la table {table_name}: {e}")
            return False
    
    def generate_loading_report(self) -> Dict:
        """Génère un rapport de chargement"""
        total_rows = sum(stat.total_rows for stat in self.stats)
        inserted_rows = sum(stat.inserted_rows for stat in self.stats)
        error_rows = sum(stat.error_rows for stat in self.stats)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'database': f"{self.config.host}:{self.config.port}/{self.config.database}",
            'total_tables': len(self.stats),
            'total_rows_processed': total_rows,
            'total_rows_inserted': inserted_rows,
            'total_errors': error_rows,
            'overall_success_rate': (inserted_rows / total_rows * 100) if total_rows > 0 else 0,
            'tables': []
        }
        
        for stat in self.stats:
            report['tables'].append({
                'table_name': stat.table_name,
                'rows_processed': stat.total_rows,
                'rows_inserted': stat.inserted_rows,
                'errors': stat.error_rows,
                'success_rate': stat.success_rate,
                'duration_seconds': stat.duration
            })
        
        return report
    
    def print_loading_summary(self):
        """Affiche un résumé du chargement"""
        print("\n" + "="*60)
        print("RAPPORT DE CHARGEMENT DWH")
        print("="*60)
        
        for stat in self.stats:
            print(f"  {stat}")
        
        report = self.generate_loading_report()
        print(f"\nTotal: {report['total_rows_inserted']}/{report['total_rows_processed']} lignes "
              f"({report['overall_success_rate']:.1f}% succès)")
        print(f"Base de données: {report['database']}")
        print("="*60) 