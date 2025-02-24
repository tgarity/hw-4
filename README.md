# Health Data API Service
Thomas Garity -- all code is written using Windsurf AI -- unless otherwise noted. All sql queries were written by Thomas.

A REST API service that provides health metrics data by ZIP code, built with Flask and SQLite. The service allows querying various health measures (like obesity rates, unemployment, etc.) for any US ZIP code.

## Project Structure

### Main Components
- `api-service/`: Directory containing the API implementation
  - `app.py`: Main API server implementation
  - `prepare_db.py`: Script to prepare the SQLite database
  - `requirements.txt`: Python package dependencies
  - `test_api.py`: API test suite
- `csv_to_sqlite.py`: Utility for converting CSV files to SQLite databases
- `test_csv_to_sqlite.py`: Test suite for the CSV converter
- `county_health_rankings.csv`: Source data for health metrics by county
- `zip_county.csv`: Source data mapping ZIP codes to counties

## API Service

### Available Health Measures
- Violent crime rate
- Unemployment
- Children in poverty
- Diabetic screening
- Mammography screening
- Preventable hospital stays
- Uninsured
- Sexually transmitted infections
- Physical inactivity
- Adult obesity
- Premature Death
- Daily fine particulate matter

### Installation and Setup
1. Install dependencies:
```bash
cd api-service
pip3 install -r requirements.txt
```

2. Prepare the database:
```bash
python3 prepare_db.py
```

### Running the API
```bash
cd api-service
python3 app.py  # Starts server on port 9000
```

### API Usage

**Endpoint:** POST /county_data

**Headers:**
- Content-Type: application/json

**Request Body:**
```json
{
    "zip": "02138",
    "measure_name": "Adult obesity"
}
```

**Example using curl:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"zip": "02138", "measure_name": "Adult obesity"}' \
  http://localhost:9000/county_data
```

**Successful Response (200 OK):**
```json
[
    {
        "raw_value": "20.5",
        "county": "Middlesex County",
        "state": "MA"
    }
]
```

### Error Responses
- 400: Invalid ZIP format or missing fields
- 404: ZIP code or measure not found
- 418: Easter egg response ({"coffee": "teapot"})

## Testing

### API Tests (`test_api.py`)
Tests the API's functionality including:
```bash
cd api-service
python3 -m unittest test_api.py -v
```

Test cases:
- Valid request handling
- ZIP code validation
- Measure name validation
- Error responses
- Content type validation
- Multiple measures for same ZIP
- Invalid input handling
- Easter egg functionality

### CSV Converter Tests (`test_csv_to_sqlite.py`)
Tests the CSV to SQLite conversion utility:
```bash
python3 test_csv_to_sqlite.py -v
```

Test cases:
- File existence checks
- Column name validation
- Row count verification
- Data type handling
- UTF-8 BOM handling
- Error conditions

## Data Processing Tools

### CSV to SQLite Converter
Converts CSV files to SQLite database format:

```bash
python3 csv_to_sqlite.py <database_name> <csv_file>
```

Features:
- Automatic table creation
- Data type inference
- Header validation
- Error handling

### Database Preparation (`prepare_db.py`)
Prepares the SQLite database for the API:
- Converts health rankings CSV to SQLite
- Converts ZIP-county mapping CSV to SQLite
- Creates necessary indices
- Validates data integrity

## Source Data Files

### County Health Rankings (`county_health_rankings.csv`)
Contains health metrics for US counties:
- Various health measures
- County and state identifiers
- Raw values for each measure

### ZIP County Mapping (`zip_county.csv`)
Maps ZIP codes to counties:
- ZIP codes
- 5-digit county FIPS codes (2 digits state + 3 digits county)
- Used for joining health data to ZIP codes

## Development Notes

### Database Schema
- `health_rankings`: Health metrics by county
- `zip_county`: ZIP code to county mappings
- Joined using state and county codes

### API Implementation (`app.py`)
- Flask-based REST API
- SQLite database backend
- JSON request/response format
- Comprehensive error handling
- Type casting for reliable joins

## Deployment

1. Set `debug=False` in production
2. Consider using a WSGI server
3. Adjust port if needed (default: 9000)
4. Ensure database file permissions
5. Regular database backups recommended

## Error Handling

The system handles:
- Invalid file formats
- Database connection issues
- Missing required fields
- Invalid data types
- Non-existent records
- Malformed requests