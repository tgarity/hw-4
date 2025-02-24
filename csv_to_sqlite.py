#!/usr/bin/env python3

# Entirelty written by claude 3.5 sonnet using Windsurf


import csv
import sqlite3
import sys
import os

def create_table_and_insert_data(db_name, csv_file):
    # Read the first row of CSV to get column names
    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        headers = next(csv_reader)  # Get the header row
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS data")
        
        # Create table using headers as column names
        # Using headers directly as they are guaranteed to be valid SQL names
        create_table_sql = f"CREATE TABLE data ({','.join(headers)})"
        cursor.execute(create_table_sql)
        
        # Create the INSERT statement
        placeholders = ','.join(['?' for _ in headers])
        insert_sql = f"INSERT INTO data ({','.join(headers)}) VALUES ({placeholders})"
        
        # Insert all rows
        cursor.executemany(insert_sql, csv_reader)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()

def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python3 csv_to_sqlite.py <database_name> <csv_file>")
        sys.exit(1)
        
    db_name = sys.argv[1]
    csv_file = sys.argv[2]
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        sys.exit(1)
    
    try:
        create_table_and_insert_data(db_name, csv_file)
        print(f"Successfully created {db_name} from {csv_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()