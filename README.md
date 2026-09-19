# FraudGuard AI: Real-Time Fraud Detection System

FraudGuard AI is an enterprise-grade, real-time Machine Learning pipeline designed to detect fraudulent financial transactions with high accuracy and ultra-low latency. Built with a focus on scalable MLOps, this project encompasses the entire lifecycle from rigorous data engineering and model calibration to a fully automated CI/CD cloud deployment.

## Architecture & Tech Stack

- **Machine Learning**: XGBoost, LightGBM, Scikit-learn, Optuna (Hyperparameter Tuning), MLflow (Experiment Tracking)
- **Data Engineering**: Pandas, NumPy, Custom Sklearn Transformers (Target Encoding, Frequency Encoding)
- **API Server**: FastAPI, Uvicorn, Pydantic (Data Validation)
- **Containerization**: Docker
- **Infrastructure as Code (IaC)**: Terraform
- **Cloud Provider (AWS)**: Elastic Container Service (ECS - Fargate), Elastic Container Registry (ECR), Application Load Balancer (ALB), CloudWatch
- **CI/CD**: GitHub Actions

## Key Features

1. **Advanced Feature Engineering**: Implemented robust target encoding, frequency encoding, and interaction features specifically tailored for highly imbalanced transactional data.
2. **Calibrated Ensemble Modeling**: Trained an optimized XGBoost champion model. Conducted rigorous hyperparameter tuning via Optuna and probability calibration to ensure reliable fraud probability outputs.
3. **Real-Time Inference API**: Deployed a lightning-fast REST API using FastAPI. Features strict Pydantic payload validation and dynamic probability thresholding for real-time `ALLOW` / `BLOCK` decisions.
4. **Serverless Cloud Deployment**: Containerized the application using Docker and deployed it to AWS ECS Fargate for auto-scaling, serverless compute. 
5. **Zero-Downtime CI/CD**: Fully automated deployment pipeline via GitHub Actions. Any push to the `main` branch automatically builds, tags, and deploys the latest Docker image to AWS with zero downtime.
6. **Infrastructure as Code**: The entire AWS infrastructure (VPC, Security Groups, ALB, ECS, ECR) is strictly defined and managed using Terraform.

## Project Structure

```bash
├── data/                  # Raw and processed transaction datasets
├── models/                # Serialized champion models (.pkl)
├── notebooks/             # EDA, Feature Selection, and Model Tuning
├── src/
│   └── fraudguard/        # Core Python package
│       ├── features/      # Custom Sklearn Transformers
│       ├── models/        # Training and evaluation scripts
│       └── api/           # FastAPI application and schemas
├── infrastructure/        # Terraform IaC definitions
├── scripts/               # Utility and API testing scripts
├── .github/workflows/     # CI/CD pipelines
├── Dockerfile             # Container definition
└── requirements.txt       # Python dependencies
```

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the API Locally
```bash
uvicorn src.fraudguard.api.main:app --host 0.0.0.0 --port 8000
```
Navigate to `http://127.0.0.1:8000/docs` to interact with the Swagger UI.

## Cloud Deployment (AWS)

1. Set AWS credentials in your environment.
2. Navigate to the `infrastructure/` directory.
3. Initialize and apply the Terraform configuration:
```bash
terraform init
terraform apply -auto-approve
```
4. Push code to GitHub to trigger the CI/CD pipeline, which will automatically deploy the API to the AWS Load Balancer.
