import boto3
import time
import json
import os

# Initialize AWS clients
sqs_client = boto3.client('sqs')
s3_client = boto3.client('s3')

# SQS Queue URL and S3 Bucket Name (replace with your values)
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
POLLING_INTERVAL = 10  # Time in seconds to wait before polling SQS again

def process_messages():
    while True:
        # Receive messages from SQS
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20  # Long polling
        )
        
        messages = response.get('Messages', [])
        
        for message in messages:
            # Process each message
            upload_to_s3(message)
            # Delete the message from the queue after processing
            sqs_client.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )
        
        time.sleep(POLLING_INTERVAL)

def upload_to_s3(message):
    # Prepare data for S3 upload
    message_body = json.loads(message['Body'])
    filename = f"{message_body['email_subject']}.json"  # Example file name
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=filename,
        Body=json.dumps(message_body)
    )
    print(f"Uploaded {filename} to S3.")

if __name__ == '__main__':
    process_messages()
