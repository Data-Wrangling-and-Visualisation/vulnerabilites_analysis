from utils.nvd_api import fetch_nvd_data

def extract():
    """Основная функция экстракции"""
    return fetch_nvd_data(days_back=1)