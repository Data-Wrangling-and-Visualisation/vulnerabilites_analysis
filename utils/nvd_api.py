import requests
import time
from datetime import datetime, timedelta
from config import NVD_API_CONFIG

def fetch_nvd_data(days_back=1):
    """Получение данных от NVD API"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        "lastModStartDate": start_date.isoformat(),
        "lastModEndDate": end_date.isoformat(),
        "resultsPerPage": NVD_API_CONFIG['resultsPerPage']
    }
    
    vulnerabilities = []
    start_index = 0
    
    while True:
        params['startIndex'] = start_index
        try:
            response = requests.get(
                NVD_API_CONFIG['base_url'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            vulnerabilities.extend(data.get('vulnerabilities', []))
            
            if len(vulnerabilities) >= data.get('totalResults', 0):
                break
                
            start_index += NVD_API_CONFIG['resultsPerPage']
            time.sleep(NVD_API_CONFIG['rate_limit_delay'])
            
        except Exception as e:
            print(f"API Error: {str(e)}")
            break
            
    return vulnerabilities