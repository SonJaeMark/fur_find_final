import sys
import os
import logging

# Ensure project root directory is in Python search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config.init import initialize_database
from core.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    filename='furfind_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("==========================================")
    print("      FurFind System Initialization       ")
    print("==========================================")
    
    try:
        # Step 1: Initialize raw database, schema, and seed data
        initialize_database()
        logging.info("Database schema and seed data checked/initialized successfully.")
        
        # Step 2: Test Singleton DatabaseManager connection
        db = DatabaseManager()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_users FROM tbl_users;")
            res = cursor.fetchone()
            print(f"[+] Singleton DB Manager verified. Total active users in DB: {res['total_users']}")
        
        print("[+] System setup completed successfully. Launching application...")
        
        from app import FurFindApp
        FurFindApp().mainloop()

    except Exception as e:
        logging.error(f"Initialization Failed: {str(e)}")
        print(f"[-] Initialization failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()