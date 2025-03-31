from datetime import datetime
import requests
import pandas as pd
import time


# API URL
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def fetch_nvd_data(start_date=None, end_date=None):
    params = {"resultsPerPage": 2000, "startIndex": 0}
    if start_date and end_date:
        params["lastModStartDate"] = start_date.isoformat()
        params["lastModEndDate"] = end_date.isoformat()

    vulnerabilities = []

    while True:
        resp = requests.get(NVD_API_URL, params=params)
        if resp.status_code != 200:
            print(f"Ошибка API: {resp.status_code}")
            break

        data = resp.json()
        items = data.get("vulnerabilities", [])
        if not items:
            break

        vulnerabilities.extend(items := data["vulnerabilities"])
        if len(vulnerabilities) >= data.get("totalResults", 0):
            break

        params["startIndex"] += MAX_RESULTS_PER_PAGE
        time.sleep(6)

    return vulnerabilities


# Example
start_date = datetime(2025, 1, 4, 0, 0, 0)
end_date = datetime(2025, 3, 4, 23, 59, 59)
vul = fetch_nvd_data(start_date, end_date)
