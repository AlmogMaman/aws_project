import boto3
import time
import json
import os
from flask import Flask, jsonify, render_template

# Initialize Flask app
app = Flask(__name__)

# Initialize AWS clients
sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION'))
s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION'))

# SQS Queue URL and S3 Bucket Name
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
POLLING_INTERVAL = os.getenv('PULL_MESSAGE_INTERVAL')

# Message count
message_count = 0

def process_messages():
    global message_count
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
            message_count += 1  # Increment the message count
            
            # Delete the message from the queue after processing
            sqs_client.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )
        
        time.sleep(POLLING_INTERVAL)

def upload_to_s3(message):
    # Prepare data for S3 upload
    message_body = json.loads(message['Body'])
    filename = f"{message_body['email_subject']}.json"
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=filename,
        Body=json.dumps(message_body)
    )
    print(f"Uploaded {filename} to S3.")

@app.route('/')
def index():
    """Display the number of messages sent to S3."""
    return render_template('index.html', message_count=message_count)

if __name__ == '__main__':
    from threading import Thread

    # Start the SQS processing in a separate thread
    Thread(target=process_messages, daemon=True).start()

    # Start the Flask web server
    app.run(host='0.0.0.0', port=81)#port=80)
