import os
from dotenv import load_dotenv

load_dotenv()

# Для PostgreSQL
DB_PARAMS = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'vulnerabilities_db')
}

# Для SQLAlchemy (Flask)
class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['database']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False