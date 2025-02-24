#!/usr/bin/env python3
import unittest
import os
from app import app

class TestCountyDataAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure Flask for testing
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def setUp(self):
        # Ensure database exists before each test
        if not os.path.exists('health_data.db'):
            subprocess.run(['python3', 'prepare_db.py'], check=True)

    def test_server_is_running(self):
        """Test that the server responds to requests"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)  # Should get 404 as we only handle POST

    def test_teapot(self):
        """Test the coffee=teapot easter egg"""
        response = self.client.post(
            '/county_data',
            json={'coffee': 'teapot', 'zip': '02138', 'measure_name': 'Adult obesity'}
        )
        self.assertEqual(response.status_code, 418)

    def test_missing_measure_name(self):
        """Test error when measure_name is missing"""
        response = self.client.post(
            '/county_data',
            json={'zip': '02138'}
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_zip(self):
        """Test error when zip is missing"""
        response = self.client.post(
            '/county_data',
            json={'measure_name': 'Adult obesity'}
        )
        self.assertEqual(response.status_code, 400)

    def test_nonexistent_zip(self):
        """Test error when zip doesn't exist"""
        response = self.client.post(
            '/county_data',
            json={'zip': '00000', 'measure_name': 'Adult obesity'}
        )
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_measure(self):
        """Test error when measure doesn't exist"""
        response = self.client.post(
            '/county_data',
            json={'zip': '02138', 'measure_name': 'NonexistentMeasure'}
        )
        self.assertEqual(response.status_code, 404)

    def test_valid_request(self):
        """Test successful request with valid data"""
        response = self.client.post(
            '/county_data',
            json={'zip': '02138', 'measure_name': 'Unemployment'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Verify response structure
        self.assertIsInstance(data, list)
        if len(data) > 0:
            first_record = data[0]
            expected_fields = {
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
            self.assertTrue(all(field in first_record for field in expected_fields))
            self.assertEqual(first_record['county'], 'Middlesex County')
            self.assertEqual(first_record['state'], 'MA')
            self.assertEqual(first_record['county_code'], '17')
            self.assertEqual(first_record['state_code'], '25')

if __name__ == '__main__':
    unittest.main()
