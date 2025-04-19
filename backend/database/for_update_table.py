#!/usr/bin/env python3
import os
import sys

# === Добавляем корень проекта в sys.path, чтобы можно было импортировать config.py ===
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

import psycopg2
from config import DB_PARAMS

def get_db_connection():
    """Создает и возвращает соединение с PostgreSQL"""
    return psycopg2.connect(
        host=DB_PARAMS['host'],
        port=int(DB_PARAMS['port']),
        user=DB_PARAMS['user'],
        password=DB_PARAMS['password'],
        database=DB_PARAMS['database']
    )

def insert_new_json_to_db(vulnerabilities):
    """
    Обновляет таблицу vulnerabilities новыми данными из NVD
    с обработкой конфликтов при дублировании CVE-ID
    """
    if not vulnerabilities:
        print("Нет данных для обновления")
        return

    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        for item in vulnerabilities:
            cve = item.get("cve", {})
            metrics = cve.get("metrics", {})
            
            # Подготовка данных для вставки
            values = (
                cve.get("id"),
                cve.get("published"),
                cve.get("lastModified"),
                cve.get("vulnStatus"),
                cve.get("descriptions", [{}])[0].get("value", ""),
                metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("baseScore"),
                metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("accessVector"),
                metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("accessComplexity"),
                metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("authentication"),
                metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("confidentialityImpact"),
                metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("integrityImpact"),
                metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("availabilityImpact"),
                metrics.get("cvssMetricV2", [{}])[0].get("baseSeverity"),
                metrics.get("cvssMetricV2", [{}])[0].get("exploitabilityScore"),
                metrics.get("cvssMetricV2", [{}])[0].get("impactScore"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseSeverity"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("vectorString"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("attackVector"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("attackComplexity"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("privilegesRequired"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("userInteraction"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("scope"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("confidentialityImpact"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("integrityImpact"),
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("availabilityImpact"),
                metrics.get("cvssMetricV31", [{}])[0].get("exploitabilityScore"),
                metrics.get("cvssMetricV31", [{}])[0].get("impactScore"),
                ", ".join([desc["value"] for weakness in cve.get("weaknesses", []) 
                         for desc in weakness.get("description", [])]),
                ", ".join([ref["url"] for ref in cve.get("references", [])])
            )
            
            # SQL-запрос для вставки/обновления данных
            query = """
                INSERT INTO vulnerabilities VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (cve_id) DO UPDATE SET
                    published_date = EXCLUDED.published_date,
                    last_modified_date = EXCLUDED.last_modified_date,
                    vuln_status = EXCLUDED.vuln_status,
                    description = EXCLUDED.description,
                    cvss_v2_base_score = EXCLUDED.cvss_v2_base_score,
                    cvss_v2_access_vector = EXCLUDED.cvss_v2_access_vector,
                    cvss_v2_access_complexity = EXCLUDED.cvss_v2_access_complexity,
                    cvss_v2_authentication = EXCLUDED.cvss_v2_authentication,
                    cvss_v2_confidentiality_impact = EXCLUDED.cvss_v2_confidentiality_impact,
                    cvss_v2_integrity_impact = EXCLUDED.cvss_v2_integrity_impact,
                    cvss_v2_availability_impact = EXCLUDED.cvss_v2_availability_impact,
                    cvss_v2_severity = EXCLUDED.cvss_v2_severity,
                    cvss_v2_exploitability_score = EXCLUDED.cvss_v2_exploitability_score,
                    cvss_v2_impact_score = EXCLUDED.cvss_v2_impact_score,
                    cvss_v3_base_score = EXCLUDED.cvss_v3_base_score,
                    cvss_v3_severity = EXCLUDED.cvss_v3_severity,
                    cvss_v3_vector = EXCLUDED.cvss_v3_vector,
                    cvss_v3_attack_vector = EXCLUDED.cvss_v3_attack_vector,
                    cvss_v3_attack_complexity = EXCLUDED.cvss_v3_attack_complexity,
                    cvss_v3_privileges_required = EXCLUDED.cvss_v3_privileges_required,
                    cvss_v3_user_interaction = EXCLUDED.cvss_v3_user_interaction,
                    cvss_v3_scope = EXCLUDED.cvss_v3_scope,
                    cvss_v3_confidentiality_impact = EXCLUDED.cvss_v3_confidentiality_impact,
                    cvss_v3_integrity_impact = EXCLUDED.cvss_v3_integrity_impact,
                    cvss_v3_availability_impact = EXCLUDED.cvss_v3_availability_impact,
                    cvss_v3_exploitability_score = EXCLUDED.cvss_v3_exploitability_score,
                    cvss_v3_impact_score = EXCLUDED.cvss_v3_impact_score,
                    cwe_str = EXCLUDED.cwe_str,
                    references_str = EXCLUDED.references_str
            """
            
            cursor.execute(query, values)
        
        connection.commit()
        print(f"Успешно обновлено {len(vulnerabilities)} записей")
        
    except psycopg2.Error as e:
        print(f"Ошибка PostgreSQL при обновлении данных: {e}")
        if connection:
            connection.rollback()
        raise
    
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        raise
        
    finally:
        if connection:
            connection.close()
