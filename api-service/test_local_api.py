#!/usr/bin/env python3
import requests
import json
import time
import sys

def test_api(base_url="http://localhost:9000"):
    """Test various API scenarios"""
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    test_cases = [
        {
            "name": "Valid Request - Adult obesity",
            "payload": {
                "zip": "02138",
                "measure_name": "Adult obesity"
            },
            "expected_status": 200
        },
        {
            "name": "Valid Request - Unemployment",
            "payload": {
                "zip": "02138",
                "measure_name": "Unemployment"
            },
            "expected_status": 200
        },
        {
            "name": "Easter Egg - Teapot",
            "payload": {
                "coffee": "teapot",
                "zip": "02138",
                "measure_name": "Adult obesity"
            },
            "expected_status": 418
        },
        {
            "name": "Invalid ZIP Code",
            "payload": {
                "zip": "00000",
                "measure_name": "Adult obesity"
            },
            "expected_status": 404
        },
        {
            "name": "Invalid Measure",
            "payload": {
                "zip": "02138",
                "measure_name": "NonexistentMeasure"
            },
            "expected_status": 404
        },
        {
            "name": "Missing ZIP",
            "payload": {
                "measure_name": "Adult obesity"
            },
            "expected_status": 400
        }
    ]
    
    results = []
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/county_data",
                headers=headers,
                json=test['payload']
            )
            
            # Check if status code matches expected
            status_match = response.status_code == test['expected_status']
            if status_match:
                print(f"✅ Status code matches: {response.status_code}")
            else:
                print(f"❌ Status code mismatch. Expected {test['expected_status']}, got {response.status_code}")
                result = {
                    "test_name": test['name'],
                    "success": False,
                    "expected_status": test['expected_status'],
                    "actual_status": response.status_code,
                    "response": response.json() if response.text else None
                }
                results.append(result)
                continue

            result = {
                "test_name": test['name'],
                "success": True,
                "expected_status": test['expected_status'],
                "actual_status": response.status_code,
                "response": response.json() if response.text and response.status_code != 418 else response.text
            }

            # For successful responses, verify the response structure
            if status_match and response.status_code == 200:
                response_data = response.json()
                if response_data:
                    required_fields = {
                        'confidence_interval_lower_bound',
                        'confidence_interval_upper_bound',
                        'county',
                        'county_code',
                        'data_release_year',
                        'denominator',
                        'fipscode',
                        'measure_id',
                        'measure_name',
                        'numerator',
                        'raw_value',
                        'state',
                        'state_code',
                        'year_span'
                    }
                    
                    first_record = response_data[0]
                    missing_fields = required_fields - set(first_record.keys())
                    
                    if missing_fields:
                        print(f"❌ Missing required fields: {missing_fields}")
                        result["success"] = False
                        result["missing_fields"] = list(missing_fields)
                    else:
                        print("✅ All required fields present")
                        # Verify specific values for Middlesex County
                        if test['payload'].get('zip') == '02138':
                            if (first_record['county'] == 'Middlesex County' and
                                first_record['state'] == 'MA' and
                                first_record['county_code'] == '17' and
                                first_record['state_code'] == '25'):
                                print("✅ Correct county data")
                            else:
                                print("❌ Incorrect county data")
                                result["success"] = False
            
            # For error responses, verify the error message if expected
            elif status_match and response.status_code not in [200, 418]:
                if 'error' in response.json():
                    print("✅ Error message present")
                else:
                    print("❌ Missing error message")
                    result["success"] = False

            # Print the response for debugging
            if response.text:
                if response.status_code == 418:
                    print(f"Response: {response.text}")
                else:
                    print(f"Response: {json.dumps(response.json() if response.text else None, indent=2)}")

            results.append(result)
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed to connect to {base_url}")
            print("Make sure your API server is running!")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            result = {
                "test_name": test['name'],
                "success": False,
                "error": str(e)
            }
            results.append(result)
    
    # Print summary
    print("\n=== Test Summary ===")
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    print(f"Passed: {passed}/{total} tests")
    
    if passed < total:
        print("\nFailed Tests:")
        for result in results:
            if not result['success']:
                print(f"- {result['test_name']}")

if __name__ == "__main__":
    # Allow custom base URL as command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:9000"
    test_api(base_url)