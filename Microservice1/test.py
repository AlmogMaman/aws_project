import unittest
from flask import json
from app import app

class Microservice1TestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client and any necessary context."""
        self.app = app.test_client()
        self.app.testing = True

    def test_valid_request(self):
        """Test a valid request to the microservice."""
        payload = {
            "data": {
                "email_subject": "Happy new year!",
                "email_sender": "John Doe",
                "email_timestream": "1693561101",
                "email_content": "Just want to say... Happy new year!!!"
            },
            "token": "$DJISA<$#45ex3RtYr"
        }
        response = self.app.post('/microservice1', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Data published to SQS successfully', response.get_data(as_text=True))

    def test_missing_data_field(self):
        """Test request with missing 'data' field."""
        payload = {
            "token": "$DJISA<$#45ex3RtYr"
        }
        response = self.app.post('/microservice1', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid request, missing or invalid "data" field', response.get_data(as_text=True))

    def test_missing_token_field(self):
        """Test request with missing 'token' field."""
        payload = {
            "data": {
                "email_subject": "Happy new year!",
                "email_sender": "John Doe",
                "email_timestream": "1693561101",
                "email_content": "Just want to say... Happy new year!!!"
            }
        }
        response = self.app.post('/microservice1', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid request, missing "token" field', response.get_data(as_text=True))

    def test_missing_email_subject(self):
        """Test request with missing 'email_subject' in data."""
        payload = {
            "data": {
                "email_sender": "John Doe",
                "email_timestream": "1693561101",
                "email_content": "Just want to say... Happy new year!!!"
            },
            "token": "$DJISA<$#45ex3RtYr"
        }
        response = self.app.post('/microservice1', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing field: email_subject in "data"', response.get_data(as_text=True))

    def test_invalid_token(self):
        """Test request with an invalid token."""
        payload = {
            "data": {
                "email_subject": "Happy new year!",
                "email_sender": "John Doe",
                "email_timestream": "1693561101",
                "email_content": "Just want to say... Happy new year!!!"
            },
            "token": "invalid_token"
        }
        response = self.app.post('/microservice1', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Invalid token', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
