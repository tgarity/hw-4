#!/usr/bin/env python3

# Entirelty written by claude 3.5 sonnet using Windsurf


import unittest
import sqlite3
import csv
import os
import subprocess

class TestCSVToSQLite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Convert both CSV files to SQLite databases
        csv_files = ['county_health_rankings.csv', 'zip_county.csv']
        cls.db_files = ['health_rankings.db', 'zip_county.db']
        
        for csv_file, db_file in zip(csv_files, cls.db_files):
            # Remove existing database if it exists
            if os.path.exists(db_file):
                os.remove(db_file)
            
            # Run the conversion script
            subprocess.run(['python3', 'csv_to_sqlite.py', db_file, csv_file], check=True)
            
        # Store CSV data for comparison
        cls.csv_data = {}
        for csv_file in csv_files:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Get headers
                # Remove BOM if present
                if headers[0].startswith('\ufeff'):
                    headers[0] = headers[0].replace('\ufeff', '')
                rows = list(reader)     # Get all rows
                cls.csv_data[csv_file] = {
                    'headers': headers,
                    'rows': rows
                }

    def get_db_info(self, db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute("SELECT * FROM data LIMIT 0")
        columns = [description[0] for description in cursor.description]
        
        # Get all rows
        cursor.execute("SELECT * FROM data")
        rows = cursor.fetchall()
        
        conn.close()
        return columns, rows

    def test_column_count(self):
        """Test that the number of columns in CSV matches the database"""
        for csv_file, db_file in zip(['county_health_rankings.csv', 'zip_county.csv'], self.db_files):
            csv_columns = len(self.csv_data[csv_file]['headers'])
            db_columns, _ = self.get_db_info(db_file)
            self.assertEqual(csv_columns, len(db_columns),
                           f"Column count mismatch in {db_file}")

    def test_column_names(self):
        """Test that column names in CSV match the database"""
        for csv_file, db_file in zip(['county_health_rankings.csv', 'zip_county.csv'], self.db_files):
            csv_columns = self.csv_data[csv_file]['headers']
            db_columns, _ = self.get_db_info(db_file)
            self.assertEqual(csv_columns, list(db_columns),
                           f"Column names mismatch in {db_file}")

    def test_row_count(self):
        """Test that the number of rows in CSV matches the database"""
        for csv_file, db_file in zip(['county_health_rankings.csv', 'zip_county.csv'], self.db_files):
            csv_rows = len(self.csv_data[csv_file]['rows'])
            _, db_rows = self.get_db_info(db_file)
            self.assertEqual(csv_rows, len(db_rows),
                           f"Row count mismatch in {db_file}")

    def test_specific_rows(self):
        """Test that specific rows in CSV match the database"""
        for csv_file, db_file in zip(['county_health_rankings.csv', 'zip_county.csv'], self.db_files):
            # Test first row, last row, and a middle row
            csv_rows = self.csv_data[csv_file]['rows']
            _, db_rows = self.get_db_info(db_file)
            
            # Convert all values to strings for comparison
            csv_rows = [[str(val) for val in row] for row in csv_rows]
            db_rows = [[str(val) for val in row] for row in db_rows]
            
            # Check first row
            self.assertEqual(csv_rows[0], list(db_rows[0]),
                           f"First row mismatch in {db_file}")
            
            # Check last row
            self.assertEqual(csv_rows[-1], list(db_rows[-1]),
                           f"Last row mismatch in {db_file}")
            
            # Check middle row
            mid_idx = len(csv_rows) // 2
            self.assertEqual(csv_rows[mid_idx], list(db_rows[mid_idx]),
                           f"Middle row mismatch in {db_file}")

    @classmethod
    def tearDownClass(cls):
        # Clean up the database files
        for db_file in cls.db_files:
            if os.path.exists(db_file):
                os.remove(db_file)

if __name__ == '__main__':
    unittest.main()
