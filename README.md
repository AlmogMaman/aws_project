# AWS Microservices Project

A production-minded example of a **two-service Python system** deployed on **AWS** with **containers**, **Infrastructure as Code**, and **CI/CD**.

> **Highlights**
> - 2 Python microservices (each with its own Dockerfile)
> - CI to build/test/lint and publish images
> - CD to deploy on AWS (ECS/EKS/EC2 — depending on infra)
> - IaC in the repo for reproducible environments

---

## Table of Contents

- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Run with Docker](#run-with-docker)
- [Environment Variables](#environment-variables)
- [CI/CD](#cicd)
- [Infrastructure](#infrastructure)
- [Observability](#observability)
- [Testing & Quality](#testing--quality)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)
- [Maintainer](#maintainer)

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

\* Shared services can include DB, cache, message broker, secrets, etc., depending on your infra setup.

---

## Repository Structure

.
├─ CI/ # Continuous Integration pipeline(s) (e.g. Jenkins/Groovy)
├─ CD/ # Continuous Delivery / deployment definitions
├─ Infrasstructure/ # Infrastructure-as-Code for AWS (name kept as-is)
├─ Microservice1/ # Python microservice #1 (app + Dockerfile + reqs)
├─ Microservice2/ # Python microservice #2 (app + Dockerfile + reqs)
├─ steps.txt # Working notes / setup steps
└─ .gitignore

yaml
Copy code

---

## Tech Stack

- **Language:** Python (APIs), possible HTML assets
- **Containers:** Docker (one image per service)
- **IaC:** Terraform or CloudFormation (see `Infrasstructure/`)
- **CI/CD:** Jenkins/Groovy or platform under `CI/` and `CD/`
- **AWS Targets:** ECS Fargate / EKS / EC2 (per infra)
- **Shell Scripts:** Utilities for build/test/deploy

---

## Quick Start

```bash
# 1) Clone
git clone https://github.com/AlmogMaman/aws_project.git
cd aws_project

# 2) (Optional) Use Python 3.10+ for local runs
python --version

# 3) Choose a service to run locally
cd Microservice1
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# 4) Start the API (pick the right command for your framework)
# FastAPI (Uvicorn):
# uvicorn app:app --host 0.0.0.0 --port 8001 --reload
# Flask:
# export FLASK_APP=app.py && flask run --host 0.0.0.0 --port 8001
# Generic:
# python app.py
Repeat for Microservice2 (usually port 8002).

Local Development
Create a virtual environment per service (Microservice1, Microservice2).

Install dependencies from each service’s requirements.txt.

Use uvicorn for FastAPI or flask run for Flask (adjust the port via env var if needed).

Hot-reload: --reload (Uvicorn) or FLASK_DEBUG=1 for Flask.

Common endpoints (suggested):

GET /health – liveness

GET /ready – readiness

GET / – basic landing/status

Run with Docker
Each service includes a Dockerfile. Build and run locally:

bash
Copy code
# Microservice1
cd Microservice1
docker build -t ms1:local .
docker run --rm -p 8001:8001 --env-file .env ms1:local

# Microservice2
cd ../Microservice2
docker build -t ms2:local .
docker run --rm -p 8002:8002 --env-file .env ms2:local
If the container listens on a different port, update the host mapping accordingly (e.g., -p 8000:8000).

Environment Variables
Create a .env file inside each microservice with the variables the app expects. Example template:

env
Copy code
# App
APP_NAME=Microservice1
APP_ENV=local
PORT=8001

# Backing services (examples)
DB_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
EXTERNAL_API_BASE=https://api.example.com

# AWS (when running in cloud)
AWS_REGION=eu-central-1
SECRET_ID=my/app/secrets
Secrets: Never commit real secrets. Use:

Local: .env (ignored by Git)

CI: pipeline secrets/credentials store

AWS: SSM Parameter Store or Secrets Manager

CI/CD
CI (CI/)
Typical stages:

Install dependencies

Lint/Format (e.g., ruff/flake8/black)

Test (pytest + coverage)

Build Docker images

Scan images (optional)

Push to registry (e.g., Amazon ECR)

If using Jenkins, see CI/ for Jenkinsfile/Groovy; if using another platform, adapt the same stages.

CD (CD/)
Common flow:

Pull image tag from the registry

Update Task Definition/Manifest

Deploy to ECS/EKS/EC2

Wait for health checks/rollout (rolling or blue/green)

Image tagging strategy (recommended):

app:gitsha for immutability

app:env-latest for convenience (dev/stage/prod)

Infrastructure
All infra is under Infrasstructure/ (name intentionally kept).

This typically covers:

Networking: VPC, subnets, NAT/IGW, security groups

Compute: ECS (Fargate) / EKS / EC2 + capacity

Routing: ALB/NLB, target groups, listeners

Registry: ECR repositories

State: Remote backend (e.g., S3 + DynamoDB for Terraform)

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
Pick the flow that matches the actual files in Infrasstructure/.

Observability
Logs: write to stdout/stderr; forward via ECS/EKS to CloudWatch Logs

Metrics: expose Prometheus endpoints or use CloudWatch custom metrics

Tracing: integrate OpenTelemetry SDKs for distributed traces

Health: container HEALTHCHECK + target group health checks

Testing & Quality
Suggested tools/commands:

bash
Copy code
# Unit tests
pytest -q

# Formatting
black .

# Linting
ruff .         # or: flake8 .

# Type checking (if annotated)
mypy .
Add these to CI to block broken commits.

Troubleshooting
Port mismatch: ensure app port == Dockerfile EXPOSE == container PORT env

Image not updating: push a new tag and update service to that tag

No outbound access: verify NAT gateway and route tables (private subnets)

Service-to-service: check SG rules, service discovery/DNS, and health checks

IAM: verify task role has access to ECR, SSM/Secrets, CloudWatch, etc.

Roadmap
 OpenAPI docs (e.g., FastAPI /docs or Swagger for Flask)

 Integration tests & contract tests

 Blue/green or canary releases

 Dashboards for metrics/traces

 Managed DB/cache layer (RDS, ElastiCache)

 Autoscaling policies (CPU/Memory/ALB-Requests)

License
If open-sourcing, add a LICENSE file (e.g., MIT).

Maintainer
Almog Maman — Issues and PRs are welcome.

makefile
Copy code
::contentReference[oaicite:0]{index=0}
