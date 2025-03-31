import json
import psycopg2

DB_PARAMS = {
    'dbname': 'nvd_cve',
    'user': '',
    'password': '',
    'host': 'localhost',
    'port': '5432'
}


def insert_json_to_db(vulnerabilities):
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            for item in vulnerabilities:
                cve = item.get("cve", {})
                metrics = cve.get("metrics", {})

                # Подготовка данных для вставки
                values = (
                    cve.get("id"),
                    cve.get("published"),
                    cve.get("lastModified"),
                    cve.get("vulnStatus"),
                    cve.get("descriptions")[0]["value"],
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
                    ", ".join([desc["value"] for weakness in cve.get("weaknesses", []) for desc in weakness["description"]]),
                    ", ".join([ref["url"] for ref in cve.get("references", [])])
                )

                cur.execute("""
                    INSERT INTO vulnerabilities VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                """, tuple(values))

            conn.commit()



JSON_FILE = "nvd_raw_data_2025-03-09.json"
with open(JSON_FILE, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

insert_json_to_db(raw_data)
