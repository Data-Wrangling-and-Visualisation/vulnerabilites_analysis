import requests
import pandas as pd
import time
from datetime import datetime
import json


# API URL
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MAX_RESULTS_PER_PAGE = 2000  
TOTAL_RESULTS = None  


def fetch_nvd_data():
    vulnerabilities = []
    start_index = 0  

    global TOTAL_RESULTS

    while True:
        params = {
            "resultsPerPage": MAX_RESULTS_PER_PAGE,
            "startIndex": start_index
        }
        
        response = requests.get(NVD_API_URL, params=params)
        if response.status_code != 200:
            print(f"Ошибка при запросе данных: {response.status_code}")
            break

        data = response.json()
        if "vulnerabilities" not in data:
            print("Нет данных.")
            break

        vulnerabilities.extend(data["vulnerabilities"])
        TOTAL_RESULTS = data.get("totalResults", len(vulnerabilities))

        print(f"Загружено {len(vulnerabilities)} из {TOTAL_RESULTS}")

        if len(vulnerabilities) >= TOTAL_RESULTS:
            break

        start_index += MAX_RESULTS_PER_PAGE
        time.sleep(6)  # Делаем паузу, чтобы не перегружать API

    return vulnerabilities


def process_nvd_data(vulnerabilities):
    if not vulnerabilities:
        print("Нет уязвимостей для обработки.")
        return pd.DataFrame()

    data_list = []
    for item in vulnerabilities:
        cve = item.get("cve", {})

        cve_id = cve.get("id", "N/A")
        published_date = cve.get("published", "N/A")
        last_modified_date = cve.get("lastModified", "N/A")
        vuln_status = cve.get("vulnStatus", "N/A")
        description = cve.get("descriptions")[0].get("value", None)

        # Метрики CVSS (используем v3.1, если есть, иначе v2.0)
        metrics = cve.get("metrics", {})

        # CVSS v2.0
        cvss_v2 = metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {})
        cvss_v2_base_score = cvss_v2.get("baseScore", None)
        cvss_v2_access_vector = cvss_v2.get("accessVector", None)
        cvss_v2_access_complexity = cvss_v2.get("accessComplexity", None)
        cvss_v2_authentication = cvss_v2.get("authentication", None)
        cvss_v2_confidentiality_impact = cvss_v2.get("confidentialityImpact", None)
        cvss_v2_integrity_impact = cvss_v2.get("integrityImpact", None)
        cvss_v2_availability_impact = cvss_v2.get("availabilityImpact", None)
        
        cvss_v2_metric = metrics.get("cvssMetricV2", [{}])[0]
        
        cvss_v2_severity = cvss_v2_metric.get("baseSeverity", None)
        cvss_v2_exploitability_score = cvss_v2_metric.get("exploitabilityScore", None)
        cvss_v2_impact_score = cvss_v2_metric.get("impactScore", None)

        
        


        # CVSS v3.1
        cvss_v3 = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
        cvss_v3_base_score = cvss_v3.get("baseScore", None)
        cvss_v3_severity = cvss_v3.get("baseSeverity", None)
        cvss_v3_vector = cvss_v3.get("vectorString", None)
        cvss_v3_attack_vector = cvss_v3.get("attackVector", None)
        cvss_v3_attack_complexity = cvss_v3.get("attackComplexity", None)
        cvss_v3_privileges_required = cvss_v3.get("privilegesRequired", None)
        cvss_v3_user_interaction = cvss_v3.get("userInteraction", None)
        cvss_v3_scope = cvss_v3.get("scope", None)
        cvss_v3_confidentiality_impact = cvss_v3.get("confidentialityImpact", None)
        cvss_v3_integrity_impact = cvss_v3.get("integrityImpact", None)
        cvss_v3_availability_impact = cvss_v3.get("availabilityImpact", None)

        cvss_v3_exploitability_score = metrics.get("cvssMetricV31", [{}])[0].get("exploitabilityScore", None)
        cvss_v3_impact_score = metrics.get("cvssMetricV31", [{}])[0].get("impactScore", None)
        
      
        cwe_list = []
        weaknesses = cve.get("weaknesses", [])
        for weakness in weaknesses:
            descriptions = weakness.get("description", [])
            for desc in descriptions:
                if desc.get("lang", "") == "en":
                    cwe_list.append(desc.get("value", "N/A"))
        cwe_str = ", ".join(cwe_list)

        references = cve.get("references", [])
        ref_links = [ref.get("url", "N/A") for ref in references]
        references_str = ", ".join(ref_links)

        data_list.append([
                    cve_id, published_date, last_modified_date, vuln_status, description, cvss_v2_base_score, 
                    cvss_v2_access_vector , cvss_v2_access_complexity,cvss_v2_authentication,cvss_v2_confidentiality_impact,
                    cvss_v2_integrity_impact,cvss_v2_availability_impact ,cvss_v2_severity, cvss_v2_exploitability_score, 
                    cvss_v2_impact_score,  cvss_v3_base_score , cvss_v3_severity, cvss_v3_vector ,  cvss_v3_attack_vector, 
                    cvss_v3_attack_complexity, cvss_v3_privileges_required , cvss_v3_user_interaction , cvss_v3_scope , 
                    cvss_v3_confidentiality_impact , cvss_v3_integrity_impact , cvss_v3_availability_impact,  
                    cvss_v3_exploitability_score , cvss_v3_impact_score, cwe_str, references_str 
        ])

    columns = [
                    "cve_id", "published_date", "last_modified_date", "vuln_status", "description", "cvss_v2_base_score", 
                    "cvss_v2_access_vector" , "cvss_v2_access_complexity","cvss_v2_authentication","cvss_v2_confidentiality_impact",
                    "cvss_v2_integrity_impact","cvss_v2_availability_impact" ,"cvss_v2_severity", "cvss_v2_exploitability_score", 
                    "cvss_v2_impact_score",  "cvss_v3_base_score" , "cvss_v3_severity", "cvss_v3_vector" ,  "cvss_v3_attack_vector", 
                    "cvss_v3_attack_complexity", "cvss_v3_privileges_required" , "cvss_v3_user_interaction" , "cvss_v3_scope" , 
                    "cvss_v3_confidentiality_impact" , "cvss_v3_integrity_impact" , "cvss_v3_availability_impact",  
                    "cvss_v3_exploitability_score" , "cvss_v3_impact_score", "cwe_str", "references_str" 
    ]
    return pd.DataFrame(data_list, columns=columns)


vulnerabilities = fetch_nvd_data()
JSON_FILE = "nvd_raw_data_2025-03-09.json"
with open(JSON_FILE, "w", encoding="utf-8") as json_file:
    json.dump(vulnerabilities, json_file, indent=4, ensure_ascii=False)



with open(JSON_FILE, "r", encoding="utf-8") as file:
        raw_data = json.load(file)
df = process_nvd_data(raw_data)
df.to_csv("nvd_raw_data_2025-03-09.csv")
