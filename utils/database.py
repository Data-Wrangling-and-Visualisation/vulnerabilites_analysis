import psycopg2
from psycopg2.extras import execute_batch
from config import DB_CONFIG

def get_connection():
    """Возвращает соединение с PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    """Создает таблицы в БД если их нет"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    cve_id TEXT PRIMARY KEY,
                    published_date TIMESTAMP,
                    last_modified_date TIMESTAMP,
                    vuln_status TEXT,
                    description TEXT,
                    cvss_v2_base_score FLOAT,
                    cvss_v2_severity TEXT,
                    cvss_v3_base_score FLOAT,
                    cvss_v3_severity TEXT,
                    cwe_ids TEXT,
                    references TEXT
                )
            """)
            conn.commit()
    finally:
        conn.close()