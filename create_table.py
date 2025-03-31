import psycopg2

DB_PARAMS = {
    'dbname': 'nvd_cve',
    'user': 'secret',
    'password': 'secret',
    'host': 'localhost',
    'port': '5432'
}

def create_table():
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    cve_id TEXT PRIMARY KEY,
                    published_date TIMESTAMP,
                    last_modified_date TIMESTAMP,
                    vuln_status TEXT,
                    description TEXT,
                    cvss_v2_base_score FLOAT,
                    cvss_v2_access_vector TEXT,
                    cvss_v2_access_complexity TEXT,
                    cvss_v2_authentication TEXT,
                    cvss_v2_confidentiality_impact TEXT,
                    cvss_v2_integrity_impact TEXT,
                    cvss_v2_availability_impact TEXT,
                    cvss_v2_severity TEXT,
                    cvss_v2_exploitability_score FLOAT,
                    cvss_v2_impact_score FLOAT,
                    cvss_v3_base_score FLOAT,
                    cvss_v3_severity TEXT,
                    cvss_v3_vector TEXT,
                    cvss_v3_attack_vector TEXT,
                    cvss_v3_attack_complexity TEXT,
                    cvss_v3_privileges_required TEXT,
                    cvss_v3_user_interaction TEXT,
                    cvss_v3_scope TEXT,
                    cvss_v3_confidentiality_impact TEXT,
                    cvss_v3_integrity_impact TEXT,
                    cvss_v3_availability_impact TEXT,
                    cvss_v3_exploitability_score FLOAT,
                    cvss_v3_impact_score FLOAT,
                    cwe_str TEXT,
                    references_str TEXT
                )
            """)
            conn.commit()



create_table()

