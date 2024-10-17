# AWS Microservices Project

This project demonstrates a microservices architecture deployed on AWS using various services including ECS, S3, SQS, and CloudFormation. The goal is to provide a scalable and reliable architecture suitable for processing and storing email-like messages.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Additional Notes](#additional-notes)

## Features

- Two microservices: one for receiving messages and another for processing them
- Message validation and token-based authentication
- Integration with AWS services (SQS, S3, Secrets Manager)
- Infrastructure as Code using CloudFormation
- CI/CD pipeline with Jenkins
- Monitoring with Prometheus and Grafana

## Architecture

This project utilizes the following AWS services:
- **ECS (Fargate)**: For hosting the microservices
- **S3**: For storing processed messages
- **SQS**: For message queuing between microservices
- **Secrets Manager**: For storing and retrieving authentication tokens
- **CloudWatch**: For logging and monitoring
- **VPC Endpoints**: For secure communication with AWS services

## Technologies Used

- AWS (ECS, S3, SQS, Secrets Manager, CloudWatch)
- Python (Flask)
- Docker
- CloudFormation
- Jenkins
- Prometheus and Grafana

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- AWS CLI
- Docker
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/aws-microservices-project.git
   cd aws-microservices-project
   ```

2. Configure AWS CLI with your credentials:
   ```bash
   aws configure
   ```

3. Ensure you have the necessary IAM permissions to create and manage the required AWS resources.

## Deployment

To deploy the application, follow these steps:

1. Navigate to the infrastructure directory:
   ```bash
   cd infrastructure
   ```

2. Create the CloudFormation stack:
   ```bash
   aws cloudformation create-stack --stack-name MyMicroservicesStack --template-body file://main.yaml --parameters file://parameters.yaml --capabilities CAPABILITY_IAM
   ```

3. Wait for the stack creation to complete. You can monitor the progress in the AWS CloudFormation console.

4. Once the stack is created, set up Jenkins using the provided instructions (not included in this README).

5. Configure Prometheus and Grafana for monitoring (instructions not included in this README).

## Usage

After deployment:

1. To send a message, use the ALB address of Microservice1. You can either:
   - Use the browser interface
   - Send a POST request with the required payload

2. Verify that Microservice2 has processed the message by checking the S3 bucket for the uploaded data.

3. Monitor the application using the Prometheus and Grafana dashboards you've set up.

## Additional Notes

- The project uses Fargate as the compute engine for ECS tasks.
- VPC Endpoints are used to ensure traffic to internal AWS services doesn't go through the public internet.
- Security best practices are implemented, including the principle of least privilege for IAM roles.
- CloudFormation templates are stored in an S3 bucket, and nested stacks are used for better organization.
- To access Jenkins, use the EC2 Instance Connect Endpoint. The initial admin password can be found at: `/var/jenkins_home/secrets/initialAdminPassword`

For more detailed instructions on running specific components or troubleshooting, please refer to the individual README files in each microservice directory.
