# config.py
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# основной URL для SQLAlchemy и psycopg2
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

# разбираем DATABASE_URL для psycopg2
if DATABASE_URL.startswith('postgres'):
    url = urlparse(DATABASE_URL)
    DB_PARAMS = {
        'host':     url.hostname,
        'port':     url.port or 5432,
        'user':     url.username,
        'password': url.password,
        'database': url.path.lstrip('/'),
    }
else:
    DB_PARAMS = {}

class Config:
    # для Flask‑SQLAlchemy
    SQLALCHEMY_DATABASE_URI        = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
