import boto3
import time
import json
import os
from flask import Flask, jsonify, render_template
import logging

# Initialize Flask app
app = Flask(__name__)

# Set Flask logging level to DEBUG
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)


# Initialize AWS clients
app.logger.info("Initializing AWS clients...")
try:
    sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION'))
    s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION'))
except Exception as e:
    app.logger.error(f"Error initializing AWS clients: {e}")
    raise e

# Load environment variables
SQS_QUEUE_URI = os.getenv('SQS_QUEUE_URI')
S3_BUCKET_URI = os.getenv('S3_BUCKET_URI')
PULL_MESSAGE_INTERVAL = int(os.getenv('PULL_MESSAGE_INTERVAL', 10))  # Default to 10 if not set

# Log the environment variables
app.logger.info(f"SQS_QUEUE_URI: {SQS_QUEUE_URI}")
app.logger.info(f"S3_BUCKET_URI: {S3_BUCKET_URI}")
app.logger.info(f"PULL_MESSAGE_INTERVAL: {PULL_MESSAGE_INTERVAL}")

# Message count
message_count = 0

def process_messages():
    global message_count
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
                    message_count += 1
                    app.logger.info(f"Rendering index page with message count: {message_count}")
                    app.logger.info(f"Message {message.get('MessageId')} processed and uploaded to S3.")

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
            Bucket=S3_BUCKET_URI,
            Key=filename,
            Body=json.dumps(message_attributes)
        )

        app.logger.info(f"Uploaded {filename} to S3 successfully.")

    except Exception as e:
        app.logger.error(f"An error occurred during S3 upload for message ID {message.get('MessageId')}: {e}")

@app.route('/get_message_count')
def get_message_count():
    """Return the current message count as a JSON response."""
    return jsonify(message_count=message_count)

@app.route('/')
def index():
    """Display the number of messages sent to S3."""
    app.logger.info(f"Rendering index page with message count: {message_count}")
    return render_template('index.html')

if __name__ == '__main__':
    from threading import Thread

    app.logger.info("Starting SQS message processor thread.")
    # Start the SQS processing in a separate thread
    Thread(target=process_messages, daemon=True).start()

    app.logger.info("Starting Flask web server.")
    # Start the Flask web server
    app.run(host='0.0.0.0', port=80, debug=True)


#OLD
# import boto3
# import time
# import json
# import os
# import threading  # Import threading for the lock
# from flask import Flask, jsonify, render_template
# import logging

# # Initialize Flask app
# app = Flask(__name__)

# #Set Flask logging level to DEBUG
# app.logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# app.logger.addHandler(handler)



# # Initialize AWS clients
# app.logger.info("Initializing AWS clients...")
# try:
#     sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION'))
#     s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION'))
# except Exception as e:
#     app.logger.error(f"Error initializing AWS clients: {e}")
#     raise e

# # Load environment variables
# SQS_QUEUE_URI = os.getenv('SQS_QUEUE_URI')
# S3_BUCKET_URI = os.getenv('S3_BUCKET_URI')
# PULL_MESSAGE_INTERVAL = int(os.getenv('PULL_MESSAGE_INTERVAL', 10))  # Default to 10 if not set

# # Log the environment variables
# app.logger.info(f"SQS_QUEUE_URI: {SQS_QUEUE_URI}")
# app.logger.info(f"S3_BUCKET_URI: {S3_BUCKET_URI}")
# app.logger.info(f"PULL_MESSAGE_INTERVAL: {PULL_MESSAGE_INTERVAL}")

# # Global message count and lock
# message_count = 0
# message_count_lock = threading.Lock()  # Create a lock for thread-safe access

# def process_messages():
#     global message_count
#     app.logger.info("Starting to process messages from SQS.")

#     while True:
#         app.logger.info("Polling for messages from SQS...")
#         try:
#             # Receive messages from SQS
#             response = sqs_client.receive_message(
#                 QueueUrl=SQS_QUEUE_URI,
#                 MaxNumberOfMessages=10,
#                 WaitTimeSeconds=20,  # Long polling
#                 AttributeNames=['All'],  # Get all system attributes
#                 MessageAttributeNames=['All']  # Get all custom message attributes
#             )
#             app.logger.info(f"SQS response: {response}")

#             messages = response.get('Messages', [])
#             app.logger.info(f"Received {len(messages)} messages.")

#             for message in messages:
#                 app.logger.info(f"Processing message ID: {message.get('MessageId')}")
#                 try:
#                     upload_to_s3(message)

#                     # Safely update the message count using a lock
#                     with message_count_lock:
#                         message_count += 1
#                         app.logger.info(f"Message {message.get('MessageId')} processed and uploaded to S3. New message count: {message_count}")

#                     # Delete the message from the queue after processing
#                     sqs_client.delete_message(
#                         QueueUrl=SQS_QUEUE_URI,
#                         ReceiptHandle=message['ReceiptHandle']
#                     )
#                     app.logger.info(f"Deleted message ID: {message.get('MessageId')} from SQS.")
#                 except Exception as e:
#                     app.logger.error(f"Error processing message ID {message.get('MessageId')}: {e}")

#             app.logger.info(f"Sleeping for {PULL_MESSAGE_INTERVAL} seconds before polling again.")
#             time.sleep(PULL_MESSAGE_INTERVAL)
#         except Exception as e:
#             app.logger.error(f"Error polling messages from SQS: {e}")
#             time.sleep(PULL_MESSAGE_INTERVAL)

# def upload_to_s3(message):
#     try:
#         app.logger.info(f"Uploading message ID: {message['MessageId']} to S3.")
        
#         # Check if MessageAttributes exist
#         if 'MessageAttributes' not in message or not message['MessageAttributes']:
#             raise ValueError('Message attributes are missing')

#         # Parse the message attributes
#         message_attributes = {}
#         for attr, attr_data in message['MessageAttributes'].items():
#             message_attributes[attr] = attr_data['StringValue']  # Assume all attributes are strings

#         app.logger.info(f"Parsed message attributes: {message_attributes}")

#         # Use the message attributes to create the filename and the content to upload
#         filename = f"{message_attributes.get('email_subject', 'unknown_subject')}-{message_attributes.get('email_sender', 'unknown_sender')}.json"
#         s3_client.put_object(
#             Bucket=S3_BUCKET_URI,
#             Key=filename,
#             Body=json.dumps(message_attributes)
#         )

#         app.logger.info(f"Uploaded {filename} to S3 successfully.")

#     except Exception as e:
#         app.logger.error(f"An error occurred during S3 upload for message ID {message.get('MessageId')}: {e}")







# @app.route('/get_message_count')
# def get_message_count():
#     """Return the current message count as a JSON response."""
#     with message_count_lock:
#         current_count = message_count  # Safely read the message count
#     return jsonify(message_count=current_count)

# @app.route('/')
# def index():
#     """Display the index page."""
#     app.logger.info("Rendering index page.")
#     return render_template('index.html')

# if __name__ == '__main__':
#     from threading import Thread

#     app.logger.info("Starting SQS message processor thread.")
#     # Start the SQS processing in a separate thread
#     Thread(target=process_messages, daemon=True).start()

#     app.logger.info("Starting Flask web server.")
#     # Start the Flask web server
#     app.run(host='0.0.0.0', port=81, debug=True)
