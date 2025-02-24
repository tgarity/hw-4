#!/usr/bin/env python3
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Configuration
DATABASE_PATH = 'health_data.db'
VALID_MEASURES = {
    'Violent crime rate',
    'Unemployment',
    'Children in poverty',
    'Diabetic screening',
    'Mammography screening',
    'Preventable hospital stays',
    'Uninsured',
    'Sexually transmitted infections',
    'Physical inactivity',
    'Adult obesity',
    'Premature Death',
    'Daily fine particulate matter'
}

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@app.route('/county_data', methods=['POST'])
def county_data():
    # Check content type
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()

    # Check for teapot easter egg
    if data.get('coffee') == 'teapot':
        return '', 418

    # Validate required fields
    zip_code = data.get('zip')
    measure_name = data.get('measure_name')

    if not zip_code or not measure_name:
        return jsonify({"error": "Both 'zip' and 'measure_name' are required"}), 400

    # Validate zip code format
    if not (zip_code.isdigit() and len(zip_code) == 5):
        return jsonify({"error": "Invalid ZIP code format"}), 400

    # Validate measure_name
    if measure_name not in VALID_MEASURES:
        return jsonify({"error": "Invalid measure_name"}), 404

    try:
        conn = get_db_connection()
        cursor = conn.cursor()


        # Query to get all health data for counties in the given ZIP code
        # JOINs on county_code, which is 5 digits in zip_county (2 digits for state + 3 for county)
        query = """
        SELECT h.*
        FROM health_rankings h
        JOIN zip_county z ON
            CAST(h.State_code AS INTEGER) = CAST(substr(CAST(z.county_code AS TEXT), 1, 2) AS INTEGER)
            AND CAST(h.County_code AS INTEGER) = CAST(substr(CAST(z.county_code AS TEXT), 3) AS INTEGER)
        WHERE z.zip = ? AND h.Measure_name = ?
        """
        
        cursor.execute(query, (zip_code, measure_name))
        rows = cursor.fetchall()
        
        # Return 404 if not found in db
        if not rows:
            return jsonify({"error": "No data found"}), 404

        # Convert rows to list of dictionaries with all columns
        result = []
        for row in rows:
            row_dict = dict(row)
            normalized_dict = {
                'confidence_interval_lower_bound': format(float(row_dict['Confidence_Interval_Lower_Bound']) if row_dict['Confidence_Interval_Lower_Bound'] else 0, '.3f'),
                'confidence_interval_upper_bound': format(float(row_dict['Confidence_Interval_Upper_Bound']) if row_dict['Confidence_Interval_Upper_Bound'] else 0, '.3f'),
                'county': row_dict['County'],
                'county_code': row_dict['County_code'],
                'data_release_year': row_dict['Data_Release_Year'],
                'denominator': format(float(row_dict['Denominator']) if row_dict['Denominator'] else 0, '.3f'),
                'fipscode': row_dict['State_code'] + row_dict['County_code'],
                'measure_id': row_dict['Measure_id'],
                'measure_name': row_dict['Measure_name'],
                'numerator': format(float(row_dict['Numerator']) if row_dict['Numerator'] else 0, '.3f'),
                'raw_value': format(float(row_dict['Raw_value']) if row_dict['Raw_value'] else 0, '.3f'),
                'state': row_dict['State'],
                'state_code': row_dict['State_code'],
                'year_span': row_dict['Year_span']
            }
            result.append(normalized_dict)
            
        return jsonify(result)

    except sqlite3.Error as e:
        return jsonify({"error": "Database error"}), 404
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Only run the development server if running locally
    import os
    if os.environ.get('VERCEL_ENV') != 'production':
        app.run(debug=True, port=9000, host='0.0.0.0')
