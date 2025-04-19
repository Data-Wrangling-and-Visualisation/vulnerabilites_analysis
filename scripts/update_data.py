#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import os, sys

# чтобы корневые модули были в PYTHONPATH
SCRIPT_DIR   = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.insert(0, PROJECT_ROOT)

from backend.api.data_fetcher          import NVDDataFetcher
from backend.database.for_update_table import insert_new_json_to_db

def main():
    parser = argparse.ArgumentParser(
        description="Update NVD CVE database"
    )
    parser.add_argument(
        '--days',
        type=int,
        default=None,
        help="Если указать N, возьмёт последние N дней; иначе — весь архив"
    )
    args = parser.parse_args()

    fetcher = NVDDataFetcher()
    if args.days is not None:
        start = datetime.now() - timedelta(days=args.days)
        end   = datetime.now()
        vulns = fetcher.fetch_data(start, end)
    else:
        vulns = fetcher.fetch_data()      # полный архив

    if vulns:
        insert_new_json_to_db(vulns)
    print(f"Updated database with {len(vulns)} vulnerabilities")

if __name__ == "__main__":
    main()
