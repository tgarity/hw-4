#!/usr/bin/env python3
import os
import sqlite3
import subprocess

def prepare_databases():
    # First, create the health rankings database using csv_to_sqlite
    subprocess.run([
        'python3', 
        '../csv_to_sqlite.py',
        'health_rankings.db',
        '../county_health_rankings.csv'
    ], check=True)
    
    # Create zip county database
    subprocess.run([
        'python3',
        '../csv_to_sqlite.py',
        'zip_county.db',
        '../zip_county.csv'
    ], check=True)
    
    # Now create our final database with both tables
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS health_rankings")
    cursor.execute("DROP TABLE IF EXISTS zip_county")
    
    # Attach both databases
    cursor.execute("ATTACH 'health_rankings.db' as health")
    cursor.execute("ATTACH 'zip_county.db' as zip")
    
    # Create health rankings table
    cursor.execute("""
    CREATE TABLE health_rankings AS 
    SELECT * FROM health.data
    """)
    
    # Create zip county table
    cursor.execute("""
    CREATE TABLE zip_county AS 
    SELECT * FROM zip.data
    """)
    
    # Create indices for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_zip ON zip_county(zip)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_county_code ON health_rankings(county_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_measure ON health_rankings(measure_name)")
    
    # Commit and cleanup
    conn.commit()
    conn.close()
    
    # Remove temporary databases
    os.remove('health_rankings.db')
    os.remove('zip_county.db')
    
    print("Database preparation complete!")

if __name__ == '__main__':
    prepare_databases()
