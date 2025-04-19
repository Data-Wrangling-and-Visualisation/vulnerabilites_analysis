import requests
from datetime import datetime, timedelta
import psycopg2
import time
from config import DB_PARAMS

from ..database.for_update_table import insert_new_json_to_db

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MAX_RESULTS_PER_PAGE = 2000
RATE_LIMIT_DELAY = 6  # seconds

class NVDDataFetcher:
    def __init__(self):
        self.last_update = self._get_last_update_time()
        
    def _get_last_update_time(self):
        """Получаем время последнего обновления из базы"""
        try:
            with psycopg2.connect(**DB_PARAMS) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT MAX(last_modified_date) FROM vulnerabilities;")
                    result = cur.fetchone()
                    return result[0] if result[0] else datetime.now() - timedelta(days=7)
        except Exception as e:
            print(f"Ошибка при получении времени последнего обновления: {e}")
            return datetime.now() - timedelta(days=7)
        
    def fetch_data(self, start_date=None, end_date=None):
        """Получение данных с NVD API"""
        params = {"resultsPerPage": MAX_RESULTS_PER_PAGE, "startIndex": 0}
        if start_date and end_date:
            params["lastModStartDate"] = start_date.isoformat()
            params["lastModEndDate"] = end_date.isoformat()

        vulnerabilities = []
        total_results = 0
        
        while True:
            try:
                response = requests.get(NVD_API_URL, params=params)
                if response.status_code != 200:
                    print(f"API Error: {response.status_code} - {response.text}")
                    break

                data = response.json()
                items = data.get("vulnerabilities", [])
                if not items:
                    break

                vulnerabilities.extend(items)
                total_results = data.get("totalResults", 0)
                print(f"Загружено {len(vulnerabilities)} из {total_results}")

                if len(vulnerabilities) >= total_results:
                    break

                params["startIndex"] += MAX_RESULTS_PER_PAGE
                time.sleep(RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"Error fetching data: {e}")
                break
                
        return vulnerabilities
    
    def update_database(self):
        """Обновление базы данных новыми уязвимостями"""
        start_date = self.last_update
        end_date = datetime.now()
        new_vulnerabilities = self.fetch_data(start_date, end_date)
        
        if new_vulnerabilities:
            insert_new_json_to_db(new_vulnerabilities)
            self.last_update = end_date
            return len(new_vulnerabilities)
        return 0