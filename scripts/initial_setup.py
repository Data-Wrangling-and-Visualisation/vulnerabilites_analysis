import subprocess
from backend.database.create_table import create_table
from backend.database.first_fill_table import insert_json_to_db
import json

def main():
    print("Running initial setup...")
    
    # 1. Create database table
    print("Creating database table...")
    create_table()
    
    # 2. Fetch initial data (optional)
    fetch_data = input("Fetch initial data from NVD API? (y/n): ").lower() == 'y'
    if fetch_data:
        print("Fetching initial data...")
        subprocess.run(["python", "scripts/get_first_data.py"])
        
        # Load and insert data
        with open("nvd_raw_data.json", "r") as f:
            data = json.load(f)
            insert_json_to_db(data)
    
    print("Setup completed successfully!")

if __name__ == "__main__":
    main()