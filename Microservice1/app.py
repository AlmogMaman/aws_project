from flask import Flask, request, jsonify
import boto3
import os

app = Flask(__name__)

# AWS clients
secret_client = boto3.client('secretsmanager')
sqs_client = boto3.client('sqs')

# SQS Queue URL (replace with your queue URL)
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

# Secret name in Secrets Manager
SECRETMANAGER_TOKEN_SECRET = 'Token'

def get_token_from_secretmanager():
    """Fetch the token from AWS Secrets Manager."""
    try:
        response = secret_client.get_secret_value(SecretId=SECRETMANAGER_TOKEN_SECRET)
        return response['SecretString']
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve secret: {str(e)}")

@app.route('/microservice1', methods=['POST'])
def process_request():


    # Extract the JSON payload
    data = request.json
    email_data = data.get('data')
    token = data.get('token')
    
    # Validate token
    stored_token = get_token_from_secretmanager()
    if token != stored_token:
        return jsonify({'error': 'Invalid token'}), 403

    # Validate that the request has necessary fields
    if not email_data or not isinstance(email_data, dict):
        return jsonify({'error': 'Invalid request, missing or invalid "data" field'}), 400
    
    # Validate specific fields in email_data
    required_fields = ['email_subject', 'email_sender', 'email_timestream', 'email_content']
    for field in required_fields:
        if field not in email_data:
            return jsonify({'error': f'Missing field: {field} in "data"'}), 400
    
    if not token:
        return jsonify({'error': 'Invalid request, missing "token" field'}), 400
    
    
    
    # Publish the data to SQS
    try:
        sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=str(email_data),
            MessageAttributes={
                'email_subject': {
                    'StringValue': email_data['email_subject'],
                    'DataType': 'String'
                },
                'email_sender': {
                    'StringValue': email_data['email_sender'],
                    'DataType': 'String'
                },
                'email_timestream': {
                    'StringValue': str(email_data['email_timestream']),
                    'DataType': 'String'
                },
                'email_content': {
                    'StringValue': email_data['email_content'],
                    'DataType': 'String'
                }
            }
        )
    except Exception as e:
        return jsonify({'error': 'Failed to send message to SQS', 'details': str(e)}), 500
    
    return jsonify({'message': 'Data published to SQS successfully'}), 200

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=8081)
