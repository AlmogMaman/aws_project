import unittest
from unittest import mock
from your_microservice_file import process_messages, upload_to_s3

class TestMicroservice2(unittest.TestCase):

    @mock.patch('your_microservice_file.sqs_client')
    @mock.patch('your_microservice_file.s3_client')
    def test_upload_to_s3(self, mock_s3, mock_sqs):
        mock_message = {
            'Body': '{"email_subject": "Test Subject", "email_sender": "sender@example.com"}'
        }
        
        upload_to_s3(mock_message)

        mock_s3.put_object.assert_called_once_with(
            Bucket='your_bucket_name',
            Key='Test Subject.json',
            Body='{"email_subject": "Test Subject", "email_sender": "sender@example.com"}'
        )

    @mock.patch('your_microservice_file.sqs_client')
    @mock.patch('your_microservice_file.s3_client')
    def test_process_messages(self, mock_s3, mock_sqs):
        mock_sqs.receive_message.return_value = {
            'Messages': [
                {
                    'Body': '{"email_subject": "Test Subject", "email_sender": "sender@example.com"}',
                    'ReceiptHandle': 'test_receipt_handle'
                }
            ]
        }

        process_messages()  # This will loop indefinitely, so you may want to use a condition or timeout.

if __name__ == '__main__':
    unittest.main()
