provider "aws" {
  region = var.aws_region
}

# 1. Amazon ECR Repository (Where the Docker Image is stored)
resource "aws_ecr_repository" "api_repo" {
  name                 = "fraudguard-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# 2. CloudWatch Log Group (Telemetry & Monitoring)
resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/ecs/fraudguard-api"
  retention_in_days = 30
}

# 3. ECS Cluster (The Orchestrator)
resource "aws_ecs_cluster" "main_cluster" {
  name = "fraudguard-cluster"
}

# 4. IAM Roles for ECS Execution (Allows ECS to pull from ECR and push to CloudWatch)
resource "aws_iam_role" "ecs_execution_role" {
  name = "fraudguard_ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 5. ECS Task Definition (The Blueprints for the Container)
resource "aws_ecs_task_definition" "api_task" {
  family                   = "fraudguard-api-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"  # 0.5 vCPU
  memory                   = "1024" # 1 GB RAM
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "fraudguard-container"
      image     = "${aws_ecr_repository.api_repo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# Note: For a true production deployment, we would also provision a VPC, Subnets, 
# Application Load Balancer (ALB), and an ECS Service to run the Task Definition continuously.
# For simplicity in this MLOps demonstration, we have provisioned the core Compute, Registry, and Monitoring.
