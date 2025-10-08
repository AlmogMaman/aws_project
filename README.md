# AWS Microservices Project

A hands-on, production-minded example of a microservices system deployed on AWS with containerization, IaC, and CI/CD.

> **Highlights**
> - 2 Python-based microservices, containerized with Docker
> - Infrastructure-as-Code for AWS (VPC, compute, and networking)
> - CI for build/test/lint; CD for image delivery & deployment
> - Clear local dev workflow and environment configuration

---

## Table of Contents

- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [Getting Started (Local)](#getting-started-local)
- [Running with Docker](#running-with-docker)
- [Environment Variables](#environment-variables)
- [CI/CD](#cicd)
- [Infrastructure](#infrastructure)
- [Observability & Logs](#observability--logs)
- [Testing & Quality](#testing--quality)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

---

## Architecture

lua
Copy code
           +-------------------------+
           |        Internet         |
           +------------+------------+
                        |
                    [ALB / NLB]
                        |
            +-----------+-----------+
            |                       |
    +-------v-------+       +-------v-------+
    | Microservice1 |       | Microservice2 |
    |  (Python API) |       |  (Python API) |
    +-------+-------+       +-------+-------+
            |                       |
            +-----------+-----------+
                        |
                 [Shared Services*]
yaml
Copy code

*Shared services may include: database, cache, message broker, or third-party APIs depending on your deployment choices.

---

## Repository Structure

.
├─ CI/ # Continuous Integration (e.g., Jenkins/Groovy or pipelines)
├─ CD/ # Continuous Delivery / deployment definitions
├─ Infrasstructure/ # Infrastructure-as-Code (AWS) [typo kept to match folder]
├─ Microservice1/ # Python microservice #1 (API + Dockerfile)
├─ Microservice2/ # Python microservice #2 (API + Dockerfile)
├─ steps.txt # Notes / setup steps used while building the project
└─ .gitignore

markdown
Copy code

> Tip: Keep the folder name `Infrasstructure` as-is unless you also update all references in CI/CD scripts.

---

## Tech Stack

- **Language:** Python (APIs), HTML (static UI if included)
- **Containers:** Docker (one image per service)
- **IaC:** Terraform or AWS CloudFormation (depending on what’s inside `Infrasstructure/`)
- **CI/CD:** Jenkins/Groovy or other pipeline definitions under `CI/` and `CD/`
- **AWS Targets:** ECS Fargate or EKS/EC2 (depending on infra definitions)
- **Shell Scripts:** Utility scripts for build/test/deploy

---

## Getting Started (Local)

> Prereqs:  
> - Python 3.10+  
> - `pip` / `venv`  
> - Docker (optional for local)  

### 1) Clone

```bash
git clone https://github.com/AlmogMaman/aws_project.git
cd aws_project
2) Setup Microservice 1
bash
Copy code
cd Microservice1
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
# Optional typical run commands:
# uvicorn app:app --host 0.0.0.0 --port 8001
# or: python app.py
3) Setup Microservice 2
bash
Copy code
cd ../Microservice2
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Optional typical run commands:
# uvicorn app:app --host 0.0.0.0 --port 8002
# or: python app.py
If the services use Flask, use flask run (after setting FLASK_APP), or a python app.py entrypoint.
If they use FastAPI, uvicorn app:app --reload is common.

Running with Docker
Each service should include its own Dockerfile.

Build & Run Microservice 1
bash
Copy code
cd Microservice1
docker build -t ms1:local .
docker run --rm -p 8001:8001 --env-file .env ms1:local
Build & Run Microservice 2
bash
Copy code
cd ../Microservice2
docker build -t ms2:local .
docker run --rm -p 8002:8002 --env-file .env ms2:local
Adjust exposed ports to match the app’s configured port (e.g., 8000/8001/8002).

Environment Variables
Create a .env file in each microservice with the variables your app expects. Common patterns:

env
Copy code
# Example .env template
APP_NAME=Microservice1
APP_ENV=local
PORT=8001

# Example backing services
DB_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
EXTERNAL_API_BASE=https://api.example.com
Never commit real secrets; prefer:

Local: .env files ignored by Git

CI: pipeline secrets/credentials store

AWS: SSM Parameter Store or AWS Secrets Manager

CI/CD
CI (CI/)
Typical pipeline stages:

Lint (flake8/ruff/black)

Unit tests (pytest)

Build Docker images (one per service)

Scan images (optional)

Push images to registry (e.g., Amazon ECR)

If you use Jenkins, look for Jenkinsfile/Groovy under CI/.
For GitHub Actions or other tools, adapt these steps to the platform syntax.

CD (CD/)
Delivery pipeline usually:

Pull image tags from ECR/registry

Update task definitions / manifests

Deploy to target (e.g., ECS Fargate service or EKS)

Health checks & rollout strategy (rolling or blue/green)

Infrastructure
Folder: Infrasstructure/ (IaC)

This typically includes:

Networking: VPC, subnets, NAT/IGW, security groups

Compute: ECS/EKS/EC2, task definitions, capacity providers

Routing: Load balancer (ALB/NLB) + target groups + listeners

Registries: ECR repositories for images

State: Remote backend for IaC state (e.g., S3 + DynamoDB for Terraform)

Terraform (if applicable)
bash
Copy code
cd Infrasstructure
terraform init
terraform workspace new dev || terraform workspace select dev
terraform plan -var-file=env/dev.tfvars
terraform apply -var-file=env/dev.tfvars
CloudFormation (if applicable)
bash
Copy code
aws cloudformation deploy \
  --stack-name aws-microservices-dev \
  --template-file template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Env=dev ImageTag=<tag>
Pick the path that matches the actual files in Infrasstructure/.

Observability & Logs
Application logs: stdout/stderr -> picked up by the container platform (e.g., CloudWatch Logs)

Metrics: add Prometheus endpoints or CloudWatch metrics as needed

Tracing: integrate OpenTelemetry (OTel) SDKs for distributed tracing

Health checks: container HEALTHCHECK and target group health checks

Testing & Quality
Unit tests: pytest -q

Formatting: black .

Linting: flake8 . or ruff .

Type checking: mypy . (if type hints are in use)

Consider adding these as CI steps to block broken commits.

Troubleshooting
Ports / binding: Ensure the container/app port matches your Dockerfile EXPOSE and .env.

Credentials: For AWS deploys, verify the CI/CD role has ECR (pull/push) and ECS/EKS update permissions.

Networking: If services can’t reach each other, check security groups, target groups, and service discovery.

Image not updating: Confirm the pipeline pushes a new tag and the service is updated to that tag.

Roadmap
 Add OpenAPI docs (FastAPI auto-docs at /docs or Swagger for Flask)

 Add integration tests

 Add blue/green or canary deploys

 Add observability stack (traces, metrics dashboards)

 Expand infra to include a managed DB and cache layer

License
Add a license file (e.g., MIT) at the repo root if you intend to open-source the code.
