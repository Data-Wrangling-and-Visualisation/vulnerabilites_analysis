#!/usr/bin/env python3
import os
import sys

# === Добавляем корень проекта в sys.path ===
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.insert(0, PROJECT_ROOT)

# Импорты уже «правильных» модулей
from backend.database.create_table       import create_table
from backend.database.first_fill_table  import insert_json_to_db
from backend.api.data_fetcher           import NVDDataFetcher

def initial_setup():
    # 1) создаём таблицу
    create_table()

    # 2) спрашиваем, нужно ли заполнять initial data
    ans = input("Fetch initial data? (y/n): ").strip().lower()
    if ans == 'y':
        json_path = input(
            "Path to initial JSON file (or leave empty to fetch from NVD API): "
        ).strip()
        
        if json_path:
            # вставляем из локального JSON
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            insert_json_to_db(raw_data)
            print(f"Успешно добавлено {len(raw_data)} записей из {json_path}")
        else:
            # скачиваем и сразу вставляем
            fetcher = NVDDataFetcher()
            count = fetcher.update_database()
            print(f"Обновлено и вставлено {count} новых уязвимостей из NVD")

if __name__ == "__main__":
    initial_setup()
