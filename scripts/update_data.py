from backend.api.data_fetcher import NVDDataFetcher
import argparse

def main():
    parser = argparse.ArgumentParser(description="Update NVD CVE database")
    parser.add_argument('--days', type=int, default=7, help="Number of days to look back for updates")
    args = parser.parse_args()
    
    fetcher = NVDDataFetcher()
    count = fetcher.update_database()
    print(f"Updated database with {count} new vulnerabilities")

if __name__ == "__main__":
    main()