from flask import Flask, request, jsonify
import boto3
import os
from datetime import datetime

app = Flask(__name__)

# AWS clients
ssm_client = boto3.client('ssm', region_name='us-east-1')
sqs_client = boto3.client('sqs', region_name='us-east-1')

# SQS Queue URL (replace with your queue URL)
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/your-account-id/your-queue-name'

# SSM Parameter name (where your token is stored)
SSM_TOKEN_PARAM = '/myapp/token'

def get_token_from_ssm():
    """Fetch the token from AWS SSM Parameter Store."""
    response = ssm_client.get_parameter(Name=SSM_TOKEN_PARAM, WithDecryption=True)
    return response['Parameter']['Value']

@app.route('/microservice1', methods=['POST'])
def process_request():
    # Extract the JSON payload
    data = request.json
    email_data = data.get('data')
    token = data.get('token')
    
    # Validate that the request has necessary fields
    if not email_data or not token:
        return jsonify({'error': 'Invalid request, missing fields'}), 400
    
    # Validate token
    stored_token = get_token_from_ssm()
    if token != stored_token:
        return jsonify({'error': 'Invalid token'}), 403
    
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
