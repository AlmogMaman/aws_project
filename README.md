# AWS Project — Microservices + CI/CD

A hands-on AWS project demonstrating a simple multi-service application with dedicated **CI** and **CD** pipelines and an **Infrastructure** folder for provisioning cloud resources.

> **Repo layout**
>
> ```
> /CI/                # build/test pipelines (Groovy/Jenkins style)
> /CD/                # deployment/release pipelines (Groovy/Jenkins style)
> /Infrasstructure/   # infrastructure-as-code and deployment assets
> /Microservice1/     # first service (Python-based)
> /Microservice2/     # second service (Python-based)
> .gitignore
> README.md
> steps.txt           # high-level manual steps / notes
> ```
>
> **Tech used (from repo language stats):** Python, HTML, Groovy, Shell, Dockerfile.

---

## ✨ What’s inside

- **Two microservices** (Python) that can be run locally or containerized.
- **Pipelines** for CI (build/test) and CD (deploy), written in Groovy (Jenkins-style).
- **Infrastructure folder** to provision cloud resources needed by the services.
- **Docker** support to package and run services consistently.

---

## 🧭 Architecture (high level)

[ Client ]
|
v
[ Microservice1 ] <--> [ Microservice2 ]
| |
+----(logs/metrics)-------+
|
v
[ AWS* ]

yaml
Copy code

> *Actual AWS services depend on what you provision (e.g., ECS/EKS/Lambda, API Gateway/ALB, S3, etc.). See `/Infrasstructure` for details.*

---

## 🚀 Quickstart

### 1) Prerequisites

- **Docker** (Desktop or Engine)
- **Python** 3.10+ (optional if running natively)
- **AWS CLI** v2 and an AWS account (optional if deploying)
- **Jenkins** (or any Groovy-compatible CI) if you want to run the pipelines

> Ensure `aws configure` is set with an account/role that has permissions to create/update the resources you plan to deploy.

---

### 2) Run locally (without Docker)

Each service is a standard Python app. From the repo root:

```bash
# Example for Microservice1
cd Microservice1
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt  # if present
python app.py  # or main.py / the module your service uses
Repeat similarly for Microservice2.

3) Run with Docker
Build images from the repo root (adjust Dockerfile paths as needed):

bash
Copy code
# Build
docker build -t microservice1 -f Microservice1/Dockerfile .
docker build -t microservice2 -f Microservice2/Dockerfile .

# Run
docker run --rm -p 8001:8000 --env-file Microservice1/.env microservice1
docker run --rm -p 8002:8000 --env-file Microservice2/.env microservice2
If you don’t have .env files, pass environment variables with multiple -e KEY=VALUE flags or update the Dockerfiles accordingly.

🏗️ Infrastructure
All cloud provisioning assets live under:

swift
Copy code
/Infrasstructure/
Typical workflow (adapt to the actual tool used there):

If using Terraform
bash
Copy code
cd Infrasstructure
terraform init
terraform plan -out plan.tfplan
terraform apply plan.tfplan
If using AWS CloudFormation / SAM
bash
Copy code
cd Infrasstructure
# Example for CloudFormation
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name aws-project-stack \
  --capabilities CAPABILITY_NAMED_IAM
Check the files in /Infrasstructure for variables, backends, or stack parameterization.

🔁 CI / CD
Pipelines are stored in:

arduino
Copy code
/CI/   # build + test (e.g., linting, unit tests, image build & push)
/CD/   # deploy (e.g., updating services / stacks)
Jenkins (example)

Point a Jenkins Multibranch Pipeline or a Pipeline job to this repo.

In Jenkins, configure credentials:

AWS credentials or role assumption (via withAWS/STS or environment vars).

Container registry (e.g., ECR) access for docker login.

Typical stages you might expect:

Checkout → Setup (Python deps)

Lint/Test (pytest/flake8/etc.)

Build Docker images

Push images to a registry

Deploy via /CD/ scripts or infra tool in /Infrasstructure

If your Jenkinsfiles reference shared libraries or specific agents, update Jenkins accordingly.

⚙️ Configuration
Create per-service environment files if not present:

bash
Copy code
Microservice1/.env
Microservice2/.env
Common variables you may need:

dotenv
Copy code
# Example
PORT=8000
LOG_LEVEL=info
# Add AWS-related settings only if your service needs them:
AWS_REGION=eu-central-1
SOME_SERVICE_ENDPOINT=https://example.internal
🧪 Testing
If tests are included with the services, run:

bash
Copy code
# Example (inside each microservice directory)
pytest -q
Add linters (e.g., flake8, ruff) and formatters (black) to your local workflow and CI.

📄 steps.txt
The repo includes a steps.txt file with additional notes or manual steps. Review it before deploying to ensure you follow any project-specific instructions.

🗂️ Project Conventions
Branching: main is deployable; feature branches for changes; PRs with CI checks.

Commits: Conventional commits recommended (e.g., feat:, fix:, chore:).

Versioning: Tag Docker images and releases with semantic versions if applicable.

✅ Health & Observability (recommended)
Structured logging (JSON) and request IDs

Container healthchecks (HEALTHCHECK in Dockerfile)

Basic /health endpoint in each service

Metrics & tracing if you deploy to AWS (e.g., CloudWatch, X-Ray)

🔒 Security (recommended)
Never commit secrets—use AWS Secrets Manager/SSM Parameter Store or CI secrets.

Principle of least privilege for IAM roles.

Scan images in CI and pin base images.

📦 Publishing (optional)
If publishing images:

bash
Copy code
aws ecr get-login-password --region $AWS_REGION \
| docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker tag microservice1:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/microservice1:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/microservice1:latest"
🧰 Troubleshooting
Pipelines fail: Check Jenkins credentials, AWS permissions, and registry logins.

Deploy fails: Re-check /Infrasstructure variables/params and AWS region.

Port conflicts: Change -p host:container when running Docker.

📝 License
Add your chosen license (MIT/Apache-2.0/etc.) at the repo root as LICENSE.

🤝 Contributing
Fork & create a feature branch

Write tests and docs

Open a PR with a clear description

🙋 Support
Open an issue or contact the repo owner if you need help.

pgsql
Copy code

*Built from the visible repo structure and language breakdown on the GitHub listing.* :contentReference[oaicite:0]{index=0}
::contentReference[oaicite:1]{index=1}
