import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    
    # Configuración de base de datos
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'rrhh_talca')
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit

    # Integracion Trilay (SQL Server, estrictamente solo lectura).
    TRILAY_SYNC_ENABLED = os.environ.get('TRILAY_SYNC_ENABLED', 'false').lower() == 'true'
    TRILAY_SQLSERVER_HOST = os.environ.get('TRILAY_SQLSERVER_HOST')
    TRILAY_SQLSERVER_PORT = int(os.environ.get('TRILAY_SQLSERVER_PORT', '1433'))
    TRILAY_SQLSERVER_DATABASE = os.environ.get('TRILAY_SQLSERVER_DATABASE', 'erp')
    TRILAY_SQLSERVER_USER = os.environ.get('TRILAY_SQLSERVER_USER')
    TRILAY_SQLSERVER_PASSWORD = os.environ.get('TRILAY_SQLSERVER_PASSWORD')
    TRILAY_SQLSERVER_DRIVER = os.environ.get('TRILAY_SQLSERVER_DRIVER', 'ODBC Driver 18 for SQL Server')
    TRILAY_SQLSERVER_ENCRYPT = os.environ.get('TRILAY_SQLSERVER_ENCRYPT', 'yes')
    TRILAY_SQLSERVER_TRUST_CERTIFICATE = os.environ.get('TRILAY_SQLSERVER_TRUST_CERTIFICATE', 'no')
    TRILAY_SYNC_INTERVAL_SECONDS = int(os.environ.get('TRILAY_SYNC_INTERVAL_SECONDS', '3600'))
