import json
import psycopg2
from config import DB_PARAMS

def insert_json_to_db(vulnerabilities):
    """Первоначальное заполнение таблицы данными"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                for item in vulnerabilities:
                    cve = item.get("cve", {})
                    metrics = cve.get("metrics", {})

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
                        ", ".join([desc["value"] for weakness in cve.get("weaknesses", []) for desc in weakness.get("description", [])]),
                        ", ".join([ref["url"] for ref in cve.get("references", [])])
                    )

                    cur.execute("""
                        INSERT INTO vulnerabilities VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, values)
                conn.commit()
        print(f"Успешно добавлено {len(vulnerabilities)} записей")
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python first_fill_table.py <путь_к_json_файлу>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
        insert_json_to_db(raw_data)
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")