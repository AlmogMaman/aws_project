import boto3
import os

# Use boto3 to interact with AWS services (S3 and SQS)
sqs_client = boto3.client('sqs', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')

# Get SQS queue URL
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/your-account-id/your-queue-name'
S3_BUCKET_NAME = 'my-bucket'

# Function to send message to SQS
def send_message_to_sqs(message):
    try:
        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=message
        )
        print(f"Message sent to SQS with ID: {response['MessageId']}")
    except Exception as e:
        print(f"Failed to send message to SQS: {str(e)}")

# Function to upload file to S3
def upload_file_to_s3(file_name, file_content):
    try:
        response = s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=file_content
        )
        print(f"File uploaded to S3: {file_name}")
    except Exception as e:
        print(f"Failed to upload file to S3: {str(e)}")

# Example usage
file_name = 'example.txt'
file_content = 'This is a test file.'

# Upload file to S3
upload_file_to_s3(file_name, file_content)

# Send message to SQS
send_message_to_sqs('File uploaded successfully.')
