import boto3
import time
import json
import os
import threading
from flask import Flask, jsonify, render_template
import logging
import queue

# Initialize Flask app
app = Flask(__name__)

# Set Flask logging level to DEBUG
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

session = boto3.Session()
credentials = session.get_credentials()
app.logger.info(f'Access Key: {credentials.access_key}')
app.logger.info(f'Secret Key: {credentials.secret_key}')
app.logger.info(f'Session Token: {credentials.token}')



# Initialize AWS clients
app.logger.info("Initializing AWS clients...")
try:
    sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION'))
    s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION'))
except Exception as e:
    app.logger.error(f"Error initializing AWS clients: {e}")
    raise e

# Load environment variables
SQS_QUEUE_URI = os.environ.get('SQS_QUEUE_URI')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
PULL_MESSAGE_INTERVAL = int(os.environ.get('PULL_MESSAGE_INTERVAL', 10))  # Default to 10 if not set

# Log the environment variables
app.logger.info(f"SQS_QUEUE_URI: {SQS_QUEUE_URI}")
app.logger.info(f"S3_BUCKET_NAME: {S3_BUCKET_NAME}")
app.logger.info(f"PULL_MESSAGE_INTERVAL: {PULL_MESSAGE_INTERVAL}")

# Queue to store the message count updates
message_count_queue = queue.Queue()

def process_messages():
    app.logger.info("Starting to process messages from SQS.")

    while True:
        app.logger.info("Polling for messages from SQS...")
        try:
            # Receive messages from SQS
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URI,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,  # Long polling
                AttributeNames=['All'],  # Get all system attributes
                MessageAttributeNames=['All']  # Get all custom message attributes
            )
            app.logger.info(f"SQS response: {response}")

            messages = response.get('Messages', [])
            app.logger.info(f"Received {len(messages)} messages.")

            for message in messages:
                app.logger.info(f"Processing message ID: {message.get('MessageId')}")
                try:
                    upload_to_s3(message)

                    # Safely increment the message count and add it to the queue
                    message_count = message_count_queue.get() if not message_count_queue.empty() else 0
                    message_count += 1
                    message_count_queue.put(message_count)
                    app.logger.info(f"Message {message.get('MessageId')} processed and uploaded to S3. New message count: {message_count}")

                    # Delete the message from the queue after processing
                    sqs_client.delete_message(
                        QueueUrl=SQS_QUEUE_URI,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    app.logger.info(f"Deleted message ID: {message.get('MessageId')} from SQS.")
                except Exception as e:
                    app.logger.error(f"Error processing message ID {message.get('MessageId')}: {e}")

            app.logger.info(f"Sleeping for {PULL_MESSAGE_INTERVAL} seconds before polling again.")
            time.sleep(PULL_MESSAGE_INTERVAL)
        except Exception as e:
            app.logger.error(f"Error polling messages from SQS: {e}")
            time.sleep(PULL_MESSAGE_INTERVAL)

def upload_to_s3(message):
    try:
        app.logger.info(f"Uploading message ID: {message['MessageId']} to S3.")
        
        # Check if MessageAttributes exist
        if 'MessageAttributes' not in message or not message['MessageAttributes']:
            raise ValueError('Message attributes are missing')

        # Parse the message attributes
        message_attributes = {}
        for attr, attr_data in message['MessageAttributes'].items():
            message_attributes[attr] = attr_data['StringValue']  # Assume all attributes are strings

        app.logger.info(f"Parsed message attributes: {message_attributes}")

        # Use the message attributes to create the filename and the content to upload
        filename = f"{message_attributes.get('email_subject', 'unknown_subject')}-{message_attributes.get('email_sender', 'unknown_sender')}.json"
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=filename,
            Body=json.dumps(message_attributes)
        )

        app.logger.info(f"Uploaded {filename} to S3 successfully.")

    except Exception as e:
        app.logger.error(f"An error occurred during S3 upload for message ID {message.get('MessageId')}: {e}")

@app.route('/get_message_count')
def get_message_count():
    """Return the current message count as a JSON response."""
    # Safely get the message count from the queue
    message_count = message_count_queue.get() if not message_count_queue.empty() else 0
    message_count_queue.put(message_count)
    return jsonify(message_count=message_count)

@app.route('/')
def index():
    """Display the index page."""
    app.logger.info("Rendering index page.")
    return render_template('index.html')

if __name__ == '__main__':
    from threading import Thread

    # Initialize the message count in the queue
    message_count_queue.put(0)

    app.logger.info("Starting SQS message processor thread.")
    # Start the SQS processing in a separate thread
    Thread(target=process_messages, daemon=True).start()

    app.logger.info("Starting Flask web server.")
    # Start the Flask web server
    app.run(host='0.0.0.0', port=80, debug=True)
