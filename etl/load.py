from utils.database import get_connection
from psycopg2.extras import execute_batch

def load(processed_data):
    """Загрузка данных в PostgreSQL"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_batch(cur,
                """
                INSERT INTO vulnerabilities VALUES (
                    %(cve_id)s, %(published_date)s, %(last_modified_date)s,
                    %(vuln_status)s, %(description)s, %(cvss_v2_base_score)s,
                    %(cvss_v2_severity)s, %(cvss_v3_base_score)s,
                    %(cvss_v3_severity)s, %(cwe_ids)s, %(references)s
                )
                ON CONFLICT (cve_id) DO UPDATE SET
                    last_modified_date = EXCLUDED.last_modified_date,
                    vuln_status = EXCLUDED.vuln_status,
                    description = EXCLUDED.description,
                    cvss_v2_base_score = EXCLUDED.cvss_v2_base_score,
                    cvss_v2_severity = EXCLUDED.cvss_v2_severity,
                    cvss_v3_base_score = EXCLUDED.cvss_v3_base_score,
                    cvss_v3_severity = EXCLUDED.cvss_v3_severity,
                    cwe_ids = EXCLUDED.cwe_ids,
                    references = EXCLUDED.references
                """,
                processed_data,
                page_size=100
            )
            conn.commit()
    finally:
        conn.close()