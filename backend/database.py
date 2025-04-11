import psycopg2
from psycopg2 import sql
from config import DB_CONFIG
import pandas as pd

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_vulnerability_stats():
    with get_connection() as conn:
        query = """
        SELECT 
            DATE_TRUNC('month', published_date) AS month,
            COUNT(*) AS count,
            AVG(cvss_v3_base_score) AS avg_score,
            cvss_v3_severity AS severity
        FROM vulnerabilities
        GROUP BY month, severity
        ORDER BY month
        """
        df = pd.read_sql(query, conn)
        return df.to_dict(orient='records')

def get_vulnerabilities_from_db(limit=100):
    with get_connection() as conn:
        query = sql.SQL("SELECT * FROM vulnerabilities ORDER BY published_date DESC LIMIT {}").format(
            sql.Literal(limit)
        )
        df = pd.read_sql(query, conn)
        return df.to_dict(orient='records')