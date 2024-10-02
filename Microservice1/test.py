import unittest
from app import app

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        # Set up the Flask app for testing
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        """Test the index route."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to My Microservice', response.data)  # Update based on your index.html content

    def test_process_request_valid(self):
        """Test valid request to /microservice1."""
        test_data = {
            'data': {
                'email_subject': 'Test Subject',
                'email_sender': 'test@example.com',
                'email_timestream': '2024-10-01T12:00:00Z',
                'email_content': 'This is a test email.'
            },
            'token': 'valid_token'  # Use a valid token for testing
        }
        response = self.app.post('/microservice1', json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Data published to SQS successfully', response.data)

    def test_process_request_invalid_token(self):
        """Test request with an invalid token."""
        test_data = {
            'data': {},
            'token': 'invalid_token'
        }
        response = self.app.post('/microservice1', json=test_data)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Invalid token', response.data)

    def test_process_request_missing_fields(self):
        """Test request with missing fields."""
        test_data = {
            'data': {'email_subject': 'Test Subject'},
            'token': 'valid_token'  # Use a valid token for testing
        }
        response = self.app.post('/microservice1', json=test_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing field: email_sender in "data"', response.data)

if __name__ == '__main__':
    unittest.main()
