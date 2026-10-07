import configparser
import os
import mysql.connector
from mysql.connector import Error

# Determine project root directory (one level up from config folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_db_config(filename=None, section='mysql'):
    if filename is None:
        filename = os.path.join(PROJECT_ROOT, 'config', 'database.ini')
        
    parser = configparser.ConfigParser()
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Configuration file '{filename}' not found.")
    parser.read(filename)
    if not parser.has_section(section):
        raise Exception(f"Section [{section}] not found in '{filename}'.")
    
    config = {param[0]: param[1] for param in parser.items(section)}
    config.pop('auth_plugin', None)
    
    # Cast port to int if present
    if 'port' in config:
        config['port'] = int(config['port'])
        
    return config

def execute_sql_script(cursor, script_path):
    if not os.path.exists(script_path):
        print(f"[-] Script path not found: {script_path}")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as file:
        sql_commands = file.read()
    
    for statement in sql_commands.split(';'):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)
    return True

def initialize_database():
    config = load_db_config()
    db_name = config.get('database', 'furfind_db')
    
    conn_params = config.copy()
    conn_params.pop('database', None)
    
    try:
        # Step 1: Connect to MySQL server & ensure DB exists
        conn = mysql.connector.connect(**conn_params)
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4;")
        print(f"[+] Database '{db_name}' verified/created successfully.")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Step 2: Connect directly to the database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Step 3: Check if schema tables exist
        cursor.execute("SHOW TABLES LIKE 'tbl_roles';")
        has_schema = cursor.fetchone() is not None
        
        if not has_schema:
            print("[*] Table schema missing. Executing schema.sql...")
            schema_path = os.path.join(PROJECT_ROOT, 'database', 'schema.sql')
            execute_sql_script(cursor, schema_path)
            conn.commit()
            print("[+] Database schema successfully created.")
        else:
            print("[+] Database schema already exists.")
            
        # Step 4: Check if seed data exists
        cursor.execute("SELECT COUNT(*) FROM tbl_roles;")
        record_count = cursor.fetchone()[0]
        
        if record_count == 0:
            print("[*] No data detected. Executing dummy.sql...")
            dummy_path = os.path.join(PROJECT_ROOT, 'database', 'dummy.sql')
            execute_sql_script(cursor, dummy_path)
            conn.commit()
            print("[+] Seed/dummy data inserted successfully.")
        else:
            print("[+] Database records already exist. Skipping seed data insertion.")

    except Error as e:
        print(f"[-] MySQL Initialization Error: {e}")
        raise e
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()