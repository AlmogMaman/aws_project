from flask import Flask, request, jsonify, render_template
import boto3
import os

app = Flask(__name__)

# AWS clients
secret_client = boto3.client('secretsmanager', region_name=os.environ.get('AWS_REGION'))
sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION'))

# SQS Queue URL
SQS_QUEUE_URI = os.environ.get('SQS_QUEUE_URI')

# Secret name in Secrets Manager
SECRETMANAGER_TOKEN_SECRET = 'Token'

def get_token_from_secretmanager():
    """Fetch the token from AWS Secrets Manager."""
    try:
        response = secret_client.get_secret_value(SecretId=SECRETMANAGER_TOKEN_SECRET)
        return response['SecretString']
    except Exception as e:
        app.logger.info(f'error: {e}')
        raise RuntimeError(f"Failed to retrieve secret: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/microservice1', methods=['POST'])
def process_request():
    # Extract the JSON payload
    payload = request.json
    data = payload.get('data')
    token = payload.get('token')

    app.logger.info(f'the payload is: {payload}')
    app.logger.info(f'the token you entered: {token}')
    app.logger.info(f'the data is: {data}')
    

    # Validate that the request has necessary fields
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid request, missing or invalid "data" field'}), 400
    
    # Validate specific fields in data
    required_fields = ['email_subject', 'email_sender', 'email_timestream', 'email_content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field} in "data"'}), 400


    # Validate token
    stored_token = get_token_from_secretmanager()
    if token != stored_token:
        return jsonify({'error': 'Invalid token'}), 403

    if not token:
        return jsonify({'error': 'Invalid request, missing "token" field'}), 400

    
    app.logger.info(f'SQS_QUEUE_URI: {SQS_QUEUE_URI}')
    # Publish the data to SQS
    try:
        sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URI,
            MessageBody=f"Message from {data.get('email_sender')}",
            MessageGroupId='default',
            MessageAttributes={
                'email_subject': {
                    'StringValue': data.get('email_subject'),
                    'DataType': 'String'
                },
                'email_sender': {
                    'StringValue': data.get('email_sender'),
                    'DataType': 'String'
                },
                'email_timestream': {
                    'StringValue': str(data.get('email_timestream')),
                    'DataType': 'String'
                },
                'email_content': {
                    'StringValue': data.get('email_content'),
                    'DataType': 'String'
                }
            }
        )
    except Exception as e:
        app.logger.info(f'error: {e}')
        return jsonify({'error': 'Failed to send message to SQS', 'details': str(e)}), 500
    
    return jsonify({'message': 'Data published to SQS successfully'}), 200

if __name__ == '__main__':
    # Run the Flask app on port 80
    app.run(host='0.0.0.0', port=80, debug=True)
